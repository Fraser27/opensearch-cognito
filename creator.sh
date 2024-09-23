#!usr/bin/bash
Green='\033[0;32m'
Red='\033[0;31m'
NC='\033[0m'

if [ -z "$1" ]
then
    infra_env='dev'
else
    infra_env=$1
fi  
# Function to prompt for input and validate it's not empty
get_input() {
    local prompt="$1"
    local var_name="$2"
    local input=""
    
    while true; do
        read -p "$prompt: " input
        if [ -n "$input" ]; then
            eval "$var_name='$input'"
            break
        else
            printf "$Red Error: Input cannot be empty. Please try again. $NC"
        fi
    done
}

# Get application_prefix from user
get_input "Enter the application prefix " application_prefix

# Get suffix from user
get_input "Enter the suffix " suffix

# Get master username
# get_input "Enter the master username for Opensearch " master_username

# Get master pwd
# get_input "Enter the master password for Opensearch " master_pwd

# Print the entered values for confirmation
printf "$Green Opensearch Domain Name: \n"
printf "$application_prefix-$suffix $NC\n" 

# Here you can add your main script logic
# For example, you might want to pass these values to another script or use them directly

# Example: Exporting variables for use in other scripts
export APPLICATION_PREFIX="$application_prefix"
export SUFFIX="$suffix"

# Example: Running another script with these parameters
# ./your_main_script.sh "$application_prefix" "$suffix"

deployment_region=$(curl -s http://169.254.169.254/task/AvailabilityZone | sed 's/\(.*\)[a-z]/\1/')
embed_model_id='cohere.embed-english-v3'
if [ -z "$deployment_region" ]
then
    printf  "$Red !!! Cannot detect region. Manually select your AWS Cloudshell region from the below list $NC"
    printf "\n"
    printf "$Green Please enter your current AWS cloudshell region (1/2/3/4/5/6): $NC"
    printf "\n"
    region_options=("N-Virginia" "Oregon" "Tokyo" "Mumbai" "Frankfurt" "Sydney" "Quit")
    select region_opts in "${region_options[@]}"
    do
        case $region_opts in 
            "N-Virginia")
                deployment_region='us-east-1'
                printf "$Green Deploy in US East(N.Virginia) $NC"
                printf "$Green Embedding model $embed_model_id $NC"
                printf "\n"
                ;; 
            "Oregon")
                deployment_region='us-west-2'
                printf "$Green Deploy in US West(Oregon) $NC"
                printf "$Green Embedding model $embed_model_id $NC"
                ;;
            # "ap-southeast-1")
            #     deployment_region='ap-southeast-1'
            #     printf "$Green Deploy in Asia Pacific (Singapore) $NC"
            #     ;;
            "Tokyo")
                deployment_region='ap-northeast-1'
                printf "$Green Deploy in Asia Pacific (Tokyo) $NC"
                embed_model_id='cohere.embed-english-v3'
                printf "$Green Embedding model $embed_model_id $NC"
                ;;
            "Mumbai")
                deployment_region='ap-south-1'
                printf "$Green Deploy in Asia Pacific (Mumbai) $NC"
                embed_model_id='cohere.embed-english-v3'
                printf "$Green Embedding model $embed_model_id $NC"
                ;;
            "Frankfurt")
                deployment_region='eu-central-1'
                printf "$Green Deploy in Europe (Frankfurt) $NC"
                printf "$Green Embedding model $embed_model_id $NC"
                ;;
            "Sydney")
                deployment_region='ap-southeast-2'
                printf "$Green Deploy in Asia Pacific (Sydney) $NC"
                embed_model_id='cohere.embed-english-v3'
                printf "$Green Embedding model $embed_model_id $NC"
                ;;
            "Quit")
                printf "$Red Quit deployment $NC"
                exit 1
                break
                ;;
            *)
            printf "$Red Exiting, Invalid option $REPLY. Select from 1/2/3/4/5/6 $NC"
            exit 1;;
        esac
        break
    done
fi
echo "Selected region: $deployment_region "

echo '*************************************************************'
echo ' '

echo '*************************************************************'
echo ' '

cd ..
echo "--- Upgrading npm ---"
sudo npm install n stable -g
echo "--- Installing cdk ---"
sudo npm install -g aws-cdk@2.91.0

echo "--- Bootstrapping CDK on account in region $deployment_region ---"
cdk bootstrap aws://$(aws sts get-caller-identity --query "Account" --output text)/$deployment_region

printf "$Green Press Enter to proceed with deployment else ctrl+c to cancel $NC "
read -p " "

cd opensearch-cognito
echo "--- pip install requirements ---"
python3 -m pip install -r requirements.txt

echo "--- CDK synthesize ---"
cdk synth -c environment_name=$infra_env -c application_prefix=$application_prefix -c suffix=$suffix

echo "--- CDK deploy ---"
cdk deploy -c environment_name=$infra_env -c application_prefix=$application_prefix -c suffix=$suffix oss-dev-OpensearchCognitoStack --require-approval never

echo "Deployment completed."
