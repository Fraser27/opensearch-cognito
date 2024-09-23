from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as _iam,
    aws_opensearchservice as _opensearch,
    aws_ec2 as _ec2,
    RemovalPolicy,
    aws_cognito as _cognito,
    aws_secretsmanager as _secretsmanager,
    # aws_sqs as sqs,
)

from constructs import Construct

class OpensearchCognitoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        env_name = self.node.try_get_context("environment_name")
        prefix = str(self.node.try_get_context("application_prefix")).lower()
        suffix = str(self.node.try_get_context("suffix")).lower()

        user_pool = _cognito.UserPool(self, f'oss-userpool-{env_name}',
            self_sign_up_enabled=False,
            sign_in_aliases=_cognito.SignInAliases(
                email=True
            ),
            auto_verify=_cognito.AutoVerifiedAttrs(
                email=True
            ),
            password_policy=_cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=False,
                require_uppercase=False,
                require_digits=False,
                require_symbols=False
            )
        )

        
        
        # Assuming 'self' is the Stack instance and 'applicationPrefix' and 'suffix' are defined
        
        # Cognito User Pool Domain
        _cognito.UserPoolDomain(self, f'oss-{env_name}-userpooldomain',
            user_pool=user_pool,
            cognito_domain=_cognito.CognitoDomainOptions(
                domain_prefix=f"{prefix}-{suffix}"
            )
        )
        
        # Cognito Identity Pool
        id_pool = _cognito.CfnIdentityPool(self, f'oss-{env_name}-identitypool',
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[]
        )
        
        # IAM Role for ES Admin User
        es_admin_user_role = _iam.Role(self, f'oss-{env_name}-esAdminUserRole',
            assumed_by=_iam.FederatedPrincipal(
                'cognito-identity.amazonaws.com',
                conditions={
                    "StringEquals": {"cognito-identity.amazonaws.com:aud": id_pool.ref},
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            )
        )
        
        # Attach roles to Identity Pool
        _cognito.CfnIdentityPoolRoleAttachment(self, f'oss-{env_name}-IDPRoleAttachment',
            identity_pool_id=id_pool.ref,
            roles={
                "authenticated": es_admin_user_role.role_arn
            }
        )
        
        # IAM Managed Policy for Opensearch HTTP
        elasticsearch_http_policy = _iam.ManagedPolicy(self, f'oss-{env_name}-HTTPPolicy',
            roles=[es_admin_user_role]
        )
        
        # IAM Role for Amazon OpenSearch Service
        es_role = _iam.Role(self, f'oss-{env_name}-esRole',
            assumed_by=_iam.ServicePrincipal('es.amazonaws.com'),
            managed_policies=[_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonESCognitoAccess')]
        )

        # Create a secret for the master user credentials
        # master_user_secret = _secretsmanager.Secret(self, f'oss{env_name}-MasterUserSecret',
        #                                             generate_secret_string=_secretsmanager.SecretStringGenerator(
        #                                                 secret_string_template='{"username": "admin"}',
        #                                                 generate_string_key="password"
        #                                                 ))
        
        # OpenSearch Domain
        es_domain = _opensearch.Domain(self, f'oss-{env_name}-domain',
            version=_opensearch.EngineVersion.OPENSEARCH_2_5,
            domain_name=prefix,
            enable_version_upgrade=True,
            removal_policy=RemovalPolicy.DESTROY,
            zone_awareness=_opensearch.ZoneAwarenessConfig(
                  availability_zone_count=3,
                  enabled=False
            ),
            
            capacity=_opensearch.CapacityConfig(
                data_nodes=1,
                data_node_instance_type='t3.small.search',
                multi_az_with_standby_enabled=False
            ),
            encryption_at_rest=_opensearch.EncryptionAtRestOptions(
                enabled=True
            ),
            
            node_to_node_encryption=True,
            enforce_https=True,
            ebs=_opensearch.EbsOptions(
                volume_size=10,
                volume_type=_ec2.EbsDeviceVolumeType.GP2
            ),
            cognito_dashboards_auth=_opensearch.CognitoOptions(role=es_role,
                                                   identity_pool_id=id_pool.ref,
                                                   user_pool_id=user_pool.user_pool_id),
            # fine_grained_access_control=_opensearch.AdvancedSecurityOptions(
            #     master_user_name=master_user_secret.secret_value_from_json("username").to_string(),
            #     master_user_password=master_user_secret.secret_value_from_json("password")
            # ),
            # access_policies=[_iam.PolicyStatement(
            #     actions=['es:*'],
            #     effect=_iam.Effect.ALLOW,
            #     principals=[_iam.AnyPrincipal()],
            #     resources=['*']
            # )]
            
        )
        # Allow the opensearch http policy full access to the domain
        elasticsearch_http_policy.add_statements(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                resources=[es_domain.domain_arn],
                actions=["es:*"]
            )
        )

        
        


        

        
