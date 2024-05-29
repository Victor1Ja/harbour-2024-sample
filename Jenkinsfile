pipeline {
    agent any

    tools {
        go 'go-1.22'
    }
    def IMAGE_NAME = UUID.randomUUID().toString()

    stages {
        stage('Build') {
            steps {
                sh 'go build main.go'
                sh 'ls -la'
                sh 'echo "Build done!!!"'
            }
        }

        stage('Deploy') {
            steps {
                sh 'echo "Deploying..."'

                withCredentials([sshUserPrivateKey(credentialsId: 'mykey2',
                                                   keyFileVariable: 'mykey',
                                                   usernameVariable: 'myuser')]) {
                    sh 'ls -la'
                    // sh 'IMAGE_NAME=$(uuidgen)'
                    sh 'echo ${IMAGE_NAME}'
                    sh 'docker push ttl.sh/${IMAGE_NAME}:1h'

                    sh "ssh vagrant@192.168.56.3 -o StrictHostKeychecking=no -i ${mykey} \"docker pull ttl.sh/${IMAGE_NAME}:1h\""
                }
            }
        }
        // stage('Run as a service') {
        //     steps {
        //         sh 'echo "Running as a service..."'
        //         withCredentials([sshUserPrivateKey(credentialsId: 'mykey2',
        //                                            keyFileVariable: 'mykey',
        //                                            usernameVariable: 'myuser')]) {

        //             // sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo docker \""


        //             // sh "scp -o StrictHostKeychecking=no -i ${mykey} myapp.service ${myuser}@192.168.56.3:"

        //             // sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo mv myapp.service /etc/systemd/system/\""
        //             // sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl daemon-reload\""
        //             // sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl start myapp\""
        //             // sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl status myapp\""
        //             // sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl enable myapp\""
        //         }
        //     }
        // }
        stage('Run as a service') {
            steps {
                sh 'echo "Running as a service..."'
                withCredentials([sshUserPrivateKey(credentialsId: 'mykey2',
                                                   keyFileVariable: 'mykey',
                                                   usernameVariable: 'myuser')]) {
                    script {
                        def remoteHost = "192.168.56.3 "
                        def imageName = "ttl.sh/${IMAGE_NAME}:1h"
                        def defaultPort = "8080"

                        def checkPortCommand = "if ! lsof -i:${defaultPort} > /dev/null; then exit 0; else exit 1; fi"
                        def stopContainerCommand = """CONTAINER_ID=\$(docker ps -q --filter "publish=${defaultPort}")
                                                    if [ ! -z "\$CONTAINER_ID" ]; then
                                                        docker stop \$CONTAINER_ID
                                                        docker rm \$CONTAINER_ID
                                                    fi"""
                        def runContainerCommandDefault = "docker run -d -p ${defaultPort}:80 --name my_container ${imageName}"

                        sshagent(['mykey2']) {
                            sh """
                            ssh -o StrictHostKeyChecking=no -i ${mykey} ${myuser}@${remoteHost} << 'EOF'
                                ${checkPortCommand}
                                if [ \$? -eq 0 ]; then
                                    ${runContainerCommandDefault}
                                else
                                    ${stopContainerCommand}
                                    ${runContainerCommandDefault}
                                fi
                            EOF
                            """
                        }
                    }
                }
            }
        }
    }
}
