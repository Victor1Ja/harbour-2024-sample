def IMAGE_NAME = UUID.randomUUID().toString()
pipeline {
    agent any

    tools {
        go 'go-1.22'
    }

    stages {
        stage('Build and Push') {
            steps {
                sh 'echo "Deploying..."'

                withCredentials([sshUserPrivateKey(credentialsId: 'mykey2',
                                                   keyFileVariable: 'mykey',
                                                   usernameVariable: 'myuser')]) {
                    script {
                        def dockerBuildCommand = "docker build -t ttl.sh/${IMAGE_NAME}:10m .";
                        def dockerPullCommand = "docker push ttl.sh/${IMAGE_NAME}:10m";
                        def ret = sh dockerBuildCommand
                        print(ret)
                        def ret1 = sh(dockerPullCommand)
                        print(ret1)
                    }    
                    
                }
            }
        }
        stage('Pull and Run as a service') {
            steps {
                sh 'echo "Running as a service..."'
                withCredentials([sshUserPrivateKey(credentialsId: 'mykey2',
                                                   keyFileVariable: 'mykey',
                                                   usernameVariable: 'myuser')]) {
                    script {
                        def remoteHost = "192.168.56.3 "
                        def imageName = "ttl.sh/${IMAGE_NAME}:10m"
                        def defaultPort = "4444"

                        def stopContainerCommand = """docker stop my_container && docker rm my_container"""
                        def runContainerCommandDefault = "docker run -d -p ${defaultPort}:${defaultPort} --name my_container ${imageName}"
                        def sshCommand = """ssh -o StrictHostKeyChecking=no -i ${mykey} ${myuser}@${remoteHost} \"${stopContainerCommand} && ${runContainerCommandDefault}\" """
                        sh(sshCommand)
                    }
                }
            }
        }
        stage('Health Check'){
            steps {
                sh 'echo "Health Check..."'
                sh '''
                RESPONSE=$(curl -s 192.168.56.3:4444/health)
                EXPECTED_RESPONSE='{"status":"healthy"}'

                if [ "$RESPONSE" = "$EXPECTED_RESPONSE" ]; then
                  echo "Service is healthy"
                else
                  echo "Service is not healthy"
                  exit 1
                fi
                '''
            }
        }
    }
}
