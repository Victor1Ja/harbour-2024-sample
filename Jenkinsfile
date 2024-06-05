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
        stage('Deploy on ec2'){
            steps{
                sh 'echo "Deploying on ec2..."'
                withCredentials([
                                sshUserPrivateKey(credentialsId: 'mykey2',
                                                   keyFileVariable: 'mykey',
                                                   usernameVariable: 'myuser'
                                                   ),
                                string(credentialsId: 'ec2Host', variable: 'ec2Host')]){
                    script {
                        print ec2Host
                        def remoteHost = "${ec2Host}"
                        print remoteHost
                        def installEnv = "python3 -m venv .env"
                        print installEnv
                        def activateEnv = "source .env/bin/activate"
                        print activateEnv
                        def installDependencies = "pip install -r requirements.txt"
                        print installDependencies
                        def runApp = "fastapi run mayn.py"
                        print runApp
                        def command = """ssh -o StrictHostKeyChecking=no -i ${mykey} ${myuser}@${remoteHost} \"${sh}&&${installEnv}&&${activateEnv}&&${installDependencies}&&${runApp}\" """
                        print command
                        print "Deploying on ec2......"
                        sh command
                    }
                }
                sh 'echo "Deployed on ec2..."'
            }
        }
    }
}
