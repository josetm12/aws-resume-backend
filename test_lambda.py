from lambda_updatevisits import lambda_handler

# Simulate API Gateway event
event = {"queryStringParameters": {"page": "home"}}

# Simulate context (not used in this example)
context = {}

# Invoke the Lambda function
response = lambda_handler(event, context)

# Print the response
print(response)
