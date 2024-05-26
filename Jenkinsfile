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

                    sh "ssh vagrant@192.168.56.3 -o StrictHostKeychecking=no -i ${mykey} \"if test -f /etc/systemd/system/myapp.service; then sudo systemctl stop myapp; fi\""

                    sh "scp -o StrictHostKeychecking=no -i ${mykey} main ${myuser}@192.168.56.3:"
                }
            }
        }
        stage('Run as a service') {
            steps {
                sh 'echo "Running as a service..."'
                withCredentials([sshUserPrivateKey(credentialsId: 'mykey2',
                                                   keyFileVariable: 'mykey',
                                                   usernameVariable: 'myuser')]) {

                    sh "scp -o StrictHostKeychecking=no -i ${mykey} myapp.service ${myuser}@192.168.56.3:"

                    sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo mv myapp.service /etc/systemd/system/\""
                    sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl daemon-reload\""
                    sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl start myapp\""
                    sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl status myapp\""
                    sh "ssh vagrant@192.168.56.3 -i ${mykey} \"sudo systemctl enable myapp\""
                }
            }
        }
    }
}
