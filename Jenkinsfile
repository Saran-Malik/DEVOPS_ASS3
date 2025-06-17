pipeline {
    agent {
        dockerfile true
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/Saran-Malik/DEVOPS_ASS3.git'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest test/test_app.py > result.log || true'
            }
        }

        stage('Get Committer Email') {
            steps {
                script {
                    COMMITTER_EMAIL = sh(script: "git --no-pager log -1 --pretty=format:'%ae'", returnStdout: true).trim()
                    echo "Committer email: ${COMMITTER_EMAIL}"
                }
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'result.log', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            script {
                def result = readFile('result.log')
                emailext (
                    subject: "Jenkins Test Result: ${currentBuild.fullDisplayName}",
                    body: "Here are the test results:\n\n${result}",
                    to: "${COMMITTER_EMAIL}"
                )
            }
        }
    }
}
