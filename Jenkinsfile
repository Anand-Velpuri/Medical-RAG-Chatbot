pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        ECR_REPO = 'my-repo'
        IMAGE_TAG = 'latest'
        SERVICE_NAME = 'llmops-medical-service'
    }

    stages {
        stage('Clone GitHub Repo') {
            steps {
                script {
                    echo 'Cloning GitHub repo to Jenkins...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Anand-Velpuri/Medical-RAG-Chatbot.git']])
                }
            }
        }

        // stage('Test EC2 SSH') {
        //         steps {
        //             sshagent(credentials: ['ec2-ssh']) {
        //                 sh '''
        //                 ssh -o StrictHostKeyChecking=no ubuntu@13.233.154.91 "
        //                     hostname
        //                     whoami
        //                 "
        //                 '''
        //             }
        //         }
        // }

        stage('Build, Scan, and Push Docker Image to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
                    script {
                        def accountId = sh(script: "aws sts get-caller-identity --query Account --output text", returnStdout: true).trim()
                        def ecrUrl = "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.ECR_REPO}"
                        def imageFullTag = "${ecrUrl}:${IMAGE_TAG}"

                        sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ecrUrl}
                        docker build -t ${env.ECR_REPO}:${IMAGE_TAG} .
                        trivy image --severity HIGH,CRITICAL --format json -o trivy-report.json ${env.ECR_REPO}:${IMAGE_TAG} || true
                        docker tag ${env.ECR_REPO}:${IMAGE_TAG} ${imageFullTag}
                        docker push ${imageFullTag}
                        """

                        archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                withCredentials([
                    file(credentialsId: 'medical-rag-env', variable: 'ENV_FILE')
                ]) {
                    sshagent(credentials: ['ec2-ssh']) {
                        script {
                            def accountId = sh(
                                script: "aws sts get-caller-identity --query Account --output text",
                                returnStdout: true
                            ).trim()

                            sh """
                            scp -o StrictHostKeyChecking=no \$ENV_FILE ubuntu@13.233.154.91:~/.env

                            ssh -o StrictHostKeyChecking=no ubuntu@13.233.154.91 '
                                aws ecr get-login-password --region ${AWS_REGION} | \
                                docker login --username AWS --password-stdin ${accountId}.dkr.ecr.${AWS_REGION}.amazonaws.com

                                docker pull ${accountId}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}

                                docker stop medical-rag || true
                                docker rm medical-rag || true

                                docker run -d \
                                    --name medical-rag \
                                    --restart always \
                                    -p 5001:5001 \
                                    --env-file ~/.env \
                                    ${accountId}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}
                            '
                            """
                        }
                    }
                }
            }
        }

        //  stage('Deploy to AWS App Runner') {
        //     steps {
        //         withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
        //             script {
        //                 def accountId = sh(script: "aws sts get-caller-identity --query Account --output text", returnStdout: true).trim()
        //                 def ecrUrl = "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.ECR_REPO}"
        //                 def imageFullTag = "${ecrUrl}:${IMAGE_TAG}"

        //                 echo "Triggering deployment to AWS App Runner..."

        //                 sh """
        //                 SERVICE_ARN=\$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='${SERVICE_NAME}'].ServiceArn" --output text --region ${AWS_REGION})
        //                 echo "Found App Runner Service ARN: \$SERVICE_ARN"

        //                 aws apprunner start-deployment --service-arn \$SERVICE_ARN --region ${AWS_REGION}
        //                 """
        //             }
        //         }
        //     }
        // }
    }
}