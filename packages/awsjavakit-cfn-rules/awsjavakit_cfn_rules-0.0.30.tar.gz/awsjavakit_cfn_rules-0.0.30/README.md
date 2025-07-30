# Additional CloudFormation Rules

## Implemented rules:

### E9001 Tags Rule:

It checks whether resources have the desired tags. Example:
```
templates:
    - tests/resources/templates/**/*.yaml
append_rules:
    - awsjavakit_cfn_rules

configure_rules:
    E9001:
        expected_tags:
            - expectedTag
```

### E9002 SQS Long polling rule:
It checks whether an SQS queue has been configured to perform long polling to avoid invoking targets with empty responses.
See https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html
 
### Suggested Usage:

Create a configuration file `.cfnlintrc` like the following:
    
```
        templates:
          - template.yaml
        append_rules:
            - awsjavakit_cfn_rules
        
        configure_rules:
            E9001:
                expected_tags:
                    - expectedTag


```
Place the configuration file in the same folder as your template (template.yaml).  
Afterwards, run the following commands

```
        python -m venv .cfn-lint-venv
        . .cfn-lint-venv/bin activate
        pip install cfn-lint
        pip install awsjavakit-cfn-rules
        
```

Finally run `cfn-lint` to run the cfn-lint.


    