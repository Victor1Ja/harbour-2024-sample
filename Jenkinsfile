def IMAGE_NAME = 'victor_fastapi_image'
pipeline {
    agent any
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
                        def remoteHost = "192.168.56.4"
                        def imageName = "ttl.sh/${IMAGE_NAME}:10m"
                        def defaultPort = "4444"

                        sh "scp -o StrictHostKeychecking=no -i ${mykey} deployment.yaml ${myuser}@192.168.56.4:"
                        // def stopContainerCommand = """docker stop my_container && docker rm my_container"""
                        // def runContainerCommandDefault = "docker run -d -p ${defaultPort}:${defaultPort} --name my_container ${imageName}"
                        // def sshCommand = """ssh -o StrictHostKeyChecking=no -i ${mykey} ${myuser}@${remoteHost} \"${stopContainerCommand} && ${runContainerCommandDefault}\" """
                        sh """
                        kind get kubeconfig --name my-cluster > kubeconfig
                        export KUBECONFIG=kubeconfig
                        kubectl apply -f deployment.yaml
                        """
                        sh(sshCommand)
                    }
                }
            }
        }
        stage('Health Check'){
            steps {
                sh 'echo "Health Check..."'
                sh '/usr/bin/curl -s 192.168.56.4:4444/health'
            }
        }
    }
}
