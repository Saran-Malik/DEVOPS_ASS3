pipeline {
    agent {
        dockerfile true
    }

    triggers {
        githubPush()
    }

    environment {
        RESULT_LOG = 'result.log'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Saran-Malik/DEVOPS_ASS3.git'
            }
        }

        stage('Test') {
            steps {
                // Run pytest and tee output so result.log is visible in Jenkins workspace
                sh 'pytest test/test_app.py | tee $RESULT_LOG || true'
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
                // Safely archive the result log
                archiveArtifacts artifacts: "${RESULT_LOG}", allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            script {
                // List files in workspace for debug (optional, helps confirm result.log is there)
                sh 'ls -la'

                // Check if result.log exists to prevent build failure
                if (fileExists("${RESULT_LOG}")) {
                    def result = readFile("${RESULT_LOG}")
                    emailext (
                        subject: "Jenkins Test Result: ${currentBuild.fullDisplayName}",
                        body: "Here are the test results:\n\n${result}",
                        to: "${COMMITTER_EMAIL}"
                    )
                } else {
                    echo "WARNING: ${RESULT_LOG} not found. Skipping email notification."
                }
            }
        }
    }
}
