#!/bin/bash
# AWS Deployment Script for BrandForge AI (Free Tier Optimized)
# This script deploys the brand generation service to AWS using ECS Fargate

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME=${CLUSTER_NAME:-brandforge-cluster}
SERVICE_NAME=${SERVICE_NAME:-brandforge-service}
TASK_DEFINITION=${TASK_DEFINITION:-brandforge-task}
ECR_REPOSITORY=${ECR_REPOSITORY:-brandforge-ai}
IMAGE_TAG=${IMAGE_TAG:-latest}
CPU=${CPU:-512}  # 0.5 vCPU (Free tier eligible)
MEMORY=${MEMORY:-1024}  # 1 GB RAM (Free tier eligible)
DESIRED_COUNT=${DESIRED_COUNT:-1}

echo "🚀 Starting AWS deployment for BrandForge AI..."
echo "Region: $AWS_REGION"
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "CPU: $CPU, Memory: $MEMORY"
echo

# Check AWS CLI authentication
echo "📋 Checking AWS authentication..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Not authenticated. Please run: aws configure"
    exit 1
fi

# Set AWS region
echo "🔧 Setting AWS region..."
export AWS_DEFAULT_REGION=$AWS_REGION

# Create ECR repository if it doesn't exist
echo "📦 Setting up ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY > /dev/null 2>&1 || {
    echo "Creating ECR repository..."
    aws ecr create-repository --repository-name $ECR_REPOSITORY
}

# Get ECR login token
echo "🔑 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push Docker image
echo "🏗️ Building and pushing Docker image..."
ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

cd /home/serah/AI-Brand-Creator

# Build optimized image for AWS free tier
docker build -t $ECR_REPOSITORY:$IMAGE_TAG \
    --build-arg TARGETPLATFORM=linux/amd64 \
    --build-arg BUILDPLATFORM=linux/amd64 \
    .

docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI
docker push $ECR_URI

if [ $? -ne 0 ]; then
    echo "❌ Image push failed!"
    exit 1
fi

echo "✅ Image pushed successfully!"

# Create ECS cluster if it doesn't exist
echo "⚙️ Setting up ECS cluster..."
aws ecs describe-clusters --clusters $CLUSTER_NAME > /dev/null 2>&1 || {
    echo "Creating ECS cluster..."
    aws ecs create-cluster --cluster-name $CLUSTER_NAME --capacity-providers FARGATE --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
}

# Create CloudWatch log group
echo "📊 Setting up CloudWatch logs..."
aws logs describe-log-groups --log-group-name-prefix /ecs/$TASK_DEFINITION > /dev/null 2>&1 || {
    echo "Creating CloudWatch log group..."
    aws logs create-log-group --log-group-name /ecs/$TASK_DEFINITION
}

# Create task execution role if it doesn't exist
echo "🔐 Setting up IAM roles..."
EXECUTION_ROLE_ARN=$(aws iam get-role --role-name ecsTaskExecutionRole --query 'Role.Arn' --output text 2>/dev/null || echo "")

if [ -z "$EXECUTION_ROLE_ARN" ]; then
    echo "Creating ECS task execution role..."
    cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
    
    aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://trust-policy.json
    aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    rm trust-policy.json
    
    EXECUTION_ROLE_ARN=$(aws iam get-role --role-name ecsTaskExecutionRole --query 'Role.Arn' --output text)
fi

# Create task definition
echo "📝 Creating ECS task definition..."
cat > task-definition.json << EOF
{
  "family": "$TASK_DEFINITION",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "$CPU",
  "memory": "$MEMORY",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "$SERVICE_NAME",
      "image": "$ECR_URI",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "false"
        },
        {
          "name": "HF_HOME",
          "value": "/tmp/hf"
        },
        {
          "name": "HUGGINGFACE_HUB_CACHE",
          "value": "/tmp/hf/hub"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$TASK_DEFINITION",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://task-definition.json > /dev/null
rm task-definition.json

# Get default VPC and subnets
echo "🌐 Setting up networking..."
DEFAULT_VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$DEFAULT_VPC_ID" --query 'Subnets[0:2].SubnetId' --output text | tr '\t' ',')

# Create security group if it doesn't exist
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SERVICE_NAME-sg" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "")

if [ "$SECURITY_GROUP_ID" = "" ] || [ "$SECURITY_GROUP_ID" = "None" ]; then
    echo "Creating security group..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name "$SERVICE_NAME-sg" --description "Security group for $SERVICE_NAME" --vpc-id $DEFAULT_VPC_ID --query 'GroupId' --output text)
    
    # Allow HTTP traffic
    aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 8080 --cidr 0.0.0.0/0
fi

# Create or update ECS service
echo "🚀 Deploying ECS service..."
SERVICE_EXISTS=$(aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --query 'services[0].serviceName' --output text 2>/dev/null || echo "")

if [ "$SERVICE_EXISTS" = "" ] || [ "$SERVICE_EXISTS" = "None" ]; then
    echo "Creating new ECS service..."
    aws ecs create-service \
        --cluster $CLUSTER_NAME \
        --service-name $SERVICE_NAME \
        --task-definition $TASK_DEFINITION \
        --desired-count $DESIRED_COUNT \
        --launch-type FARGATE \
        --platform-version LATEST \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}"
else
    echo "Updating existing ECS service..."
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --task-definition $TASK_DEFINITION \
        --desired-count $DESIRED_COUNT
fi

# Wait for service to be stable
echo "⏳ Waiting for service to be stable..."
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME

# Get service endpoint
echo "🔍 Getting service information..."
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --query 'taskArns[0]' --output text)
PUBLIC_IP=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].Association.PublicIp' --output text 2>/dev/null || echo "")

echo
echo "🎉 AWS deployment successful!"
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "Task Definition: $TASK_DEFINITION"
echo "Region: $AWS_REGION"

if [ "$PUBLIC_IP" != "" ] && [ "$PUBLIC_IP" != "None" ]; then
    echo "Service URL: http://$PUBLIC_IP:8080"
    echo
    echo "Test the API:"
    echo "curl http://$PUBLIC_IP:8080/health"
else
    echo "⚠️  Public IP not yet available. Check ECS console for service status."
fi

echo
echo "🔗 AWS Console Links:"
echo "ECS Service: https://console.aws.amazon.com/ecs/home?region=$AWS_REGION#/clusters/$CLUSTER_NAME/services/$SERVICE_NAME/details"
echo "CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logStream:group=/ecs/$TASK_DEFINITION"
echo "ECR Repository: https://console.aws.amazon.com/ecr/repositories/$ECR_REPOSITORY?region=$AWS_REGION"
echo
echo "✅ AWS deployment completed!"
