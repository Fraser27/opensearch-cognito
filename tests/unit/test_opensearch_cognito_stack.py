import aws_cdk as core
import aws_cdk.assertions as assertions

from opensearch_cognito.opensearch_cognito_stack import OpensearchCognitoStack

# example tests. To run these tests, uncomment this file along with the example
# resource in opensearch_cognito/opensearch_cognito_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = OpensearchCognitoStack(app, "opensearch-cognito")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
