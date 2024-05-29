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
                        // sshagent(['mykey2']) {
                        //     sh """
                        //     ssh -o StrictHostKeyChecking=no -i ${mykey} ${myuser}@${remoteHost} << 'EOF'
                        //         ${dockerBuildCommand}
                        //         ${dockerPullCommand}
                        //     EOF
                        //     """
                        // }


                    }    
                    
                    // sh 'ls -la'
                    // // sh 'IMAGE_NAME=$(uuidgen)'
                    // sh 'echo ${IMAGE_NAME}'
                    // sh 'docker push ttl.sh/${IMAGE_NAME}:10m'

                    // sh "ssh vagrant@192.168.56.3 -o StrictHostKeychecking=no -i ${mykey} \"docker pull ttl.sh/${IMAGE_NAME}:10m\""
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

                        def stopContainerCommand = """CONTAINER_ID=\$(docker ps -q --filter "publish=${defaultPort}")
                                                    if [ ! -z "\$CONTAINER_ID" ]; then
                                                        docker stop \$CONTAINER_ID
                                                        docker rm \$CONTAINER_ID
                                                    fi"""
                        def runContainerCommandDefault = "docker run -d -p ${defaultPort}:${defaultPort} --name my_container ${imageName}"
                        def checkPortCommand = "if ! lsof -i:${defaultPort} > /dev/null; then ${stopContainerCommand} ;fi"
                        def sshCommand = """ssh -o StrictHostKeyChecking=no -i ${mykey} ${myuser}@${remoteHost}<<${checkPortCommand} &&${runContainerCommandDefault}"""
                        sh(sshCommand)
                        """
                        // sshagent(['mykey2']) {
                        //     sh """
                        //     ssh -o StrictHostKeyChecking=no -i ${mykey} ${myuser}@${remoteHost} << 'EOF'
                        //         ${checkPortCommand}
                        //         if [ \$? -eq 0 ]; then
                        //             ${runContainerCommandDefault}
                        //         else
                        //             ${stopContainerCommand}
                        //             ${runContainerCommandDefault}
                        //         fi
                        //     EOF
                        //     """
                        // }
                    }
                }
            }
        }
    }
}
