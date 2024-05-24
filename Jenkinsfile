pipeline {
    agent any

    tools {
        go 'go-1.22'
    }

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

                    sh "ssh root@192.168.56.3 -i /var/jenkins_home/.key/id_rsa \"if test -f /etc/systemd/system/myapp.service; then systemctl stop myapp; fi\""

                    sh "scp -o StrictHostKeychecking=no -i /var/jenkins_home/.key/id_rsa main ${myuser}@192.168.56.3:"
                }
            }
        }
        stage('Run as a service') {
            steps {
                sh 'echo "Running as a service..."'
                withCredentials([sshUserPrivateKey(credentialsId: 'mykey2',
                                                   keyFileVariable: 'mykey',
                                                   usernameVariable: 'myuser')]) {

                    sh "scp -o StrictHostKeychecking=no -i /var/jenkins_home/.key/id_rsa myapp.service ${myuser}@192.168.56.3:"

                    sh "ssh root@192.168.56.3 -i /var/jenkins_home/.key/id_rsa \"sudo mv myapp.service /etc/systemd/system/\""
                    sh "ssh root@192.168.56.3 -i /var/jenkins_home/.key/id_rsa \"sudo systemctl daemon-reload\""
                    sh "ssh root@192.168.56.3 -i /var/jenkins_home/.key/id_rsa \"sudo systemctl start myapp\""
                    sh "ssh root@192.168.56.3 -i /var/jenkins_home/.key/id_rsa \"sudo systemctl status myapp\""
                    sh "ssh root@192.168.56.3 -i /var/jenkins_home/.key/id_rsa \"sudo systemctl enable myapp\""
                }
            }
        }
    }
}
