#!/usr/bin/env python3
"""
Pre-deployment check script for Certification Coupon Hunter
"""

import boto3
import json
import sys
import os
from botocore.exceptions import ClientError, NoCredentialsError

def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
                    os.environ[key] = value
    except FileNotFoundError:
        print("Warning: .env file not found. Using system environment variables.")
    return env_vars

def check_aws_credentials():
    """Check AWS credentials and account"""
    print("1. Checking AWS credentials...")
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        account_id = identity['Account']
        user_arn = identity['Arn']
        
        print(f"   ✓ AWS Account ID: {account_id}")
        print(f"   ✓ User/Role: {user_arn}")
        
        # Check if account matches expected
        expected_account = os.environ.get('AWS_ACCOUNT_ID', 'YOUR_AWS_ACCOUNT_ID')
        if account_id != expected_account:
            print(f"   Warning: Current account ({account_id}) doesn't match expected ({expected_account})")
        
        return True
        
    except NoCredentialsError:
        print("   AWS credentials not configured")
        print("   Run: aws configure")
        return False
    except Exception as e:
        print(f"   AWS credentials error: {e}")
        return False

def check_bedrock_access():
    """Check Bedrock model access"""
    print("2. Checking Bedrock access...")
    
    try:
        bedrock = boto3.client('bedrock', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        
        # List foundation models to check access
        response = bedrock.list_foundation_models()
        
        # Check if Claude 3 Sonnet is available
        claude_available = False
        for model in response.get('modelSummaries', []):
            if 'claude-3-sonnet' in model.get('modelId', ''):
                claude_available = True
                print(f"   ✓ Claude 3 Sonnet available: {model['modelId']}")
                break
        
        if not claude_available:
            print("   Claude 3 Sonnet not found. You may need to request model access.")
            print("   Go to: AWS Console → Bedrock → Model access")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("   Bedrock access denied")
            print("   Go to: AWS Console → Bedrock → Model access → Request access")
        else:
            print(f"   Bedrock error: {e}")
        return False
    except Exception as e:
        print(f"   Bedrock check failed: {e}")
        return False

def check_cdk_bootstrap():
    """Check if CDK is bootstrapped"""
    print("3. Checking CDK bootstrap...")
    
    try:
        cf = boto3.client('cloudformation')
        
        # Check for CDK bootstrap stack
        try:
            cf.describe_stacks(StackName='CDKToolkit')
            print("   ✓ CDK is bootstrapped")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                print("   CDK not bootstrapped")
                print("   Run: cdk bootstrap")
                return False
            else:
                raise e
                
    except Exception as e:
        print(f"   CDK bootstrap check failed: {e}")
        return False

def check_existing_stacks():
    """Check for existing stacks"""
    print("4. Checking existing stacks...")
    
    try:
        cf = boto3.client('cloudformation')
        
        stack_names = [
            os.environ.get('STACK_NAME', 'CertificationHunterStack'),
            os.environ.get('AGENT_STACK_NAME', 'CertificationHunterAgentStack')
        ]
        
        for stack_name in stack_names:
            try:
                response = cf.describe_stacks(StackName=stack_name)
                stack_status = response['Stacks'][0]['StackStatus']
                print(f"   Stack {stack_name} exists with status: {stack_status}")
                
                if 'FAILED' in stack_status:
                    print(f"   Stack {stack_name} is in failed state. Consider deleting it first.")
                    
            except ClientError as e:
                if e.response['Error']['Code'] == 'ValidationError':
                    print(f"   ✓ Stack {stack_name} doesn't exist (ready for deployment)")
                else:
                    raise e
        
        return True
        
    except Exception as e:
        print(f"   Stack check failed: {e}")
        return False

def check_cdk_specifically():
    """Special check for CDK since it can be installed in different ways"""
    import subprocess
    import platform
    
    # Try different ways to find CDK
    cdk_commands = [
        ['cdk', '--version'],
        ['npx', 'cdk', '--version'],
        ['npx', 'aws-cdk', '--version'],
        ['aws-cdk', '--version']
    ]
    
    # On Windows, also try with .cmd extension
    if platform.system() == 'Windows':
        cdk_commands.extend([
            ['cdk.cmd', '--version'],
            ['aws-cdk.cmd', '--version']
        ])
    
    for cmd in cdk_commands:
        try:
            # On Windows, use shell=True to handle PATH properly
            shell_needed = platform.system() == 'Windows'
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=shell_needed)
            if result.returncode == 0:
                version_output = result.stdout.strip() or result.stderr.strip()
                if version_output:
                    version_parts = version_output.split()
                    version = version_parts[0] if version_parts else version_output
                    return True, version, ' '.join(cmd)
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            continue
    
    return False, None, None

def check_required_tools():
    """Check required tools are installed"""
    print("5. Checking required tools...")
    
    tools = {
        'python': ['python', '--version'],
        'aws': ['aws', '--version'],
        'node': ['node', '--version']
    }
    
    all_good = True
    
    for tool, command in tools.items():
        try:
            import subprocess
            import platform
            # On Windows, use shell=True to handle PATH properly
            shell_needed = platform.system() == 'Windows'
            result = subprocess.run(command, capture_output=True, text=True, timeout=10, shell=shell_needed)
            if result.returncode == 0:
                # Get version from stdout or stderr
                version_output = result.stdout.strip() or result.stderr.strip()
                
                # Handle different version output formats
                if tool == 'cdk':
                    # CDK version format: "2.102.9.2 (build fccc5f9)"
                    if version_output:
                        # Extract just the version number
                        version_parts = version_output.split()
                        if len(version_parts) >= 1:
                            version = version_parts[0]
                        else:
                            version = version_output
                        print(f"   ✓ {tool}: {version}")
                    else:
                        print(f"   ✓ {tool}: installed")
                elif tool == 'python':
                    # Python version format: "Python 3.11.0"
                    version = version_output.replace('Python ', '') if 'Python' in version_output else version_output
                    print(f"   ✓ {tool}: {version}")
                elif tool == 'aws':
                    # AWS CLI version format: "aws-cli/2.x.x Python/3.x.x"
                    if 'aws-cli/' in version_output:
                        version = version_output.split()[0].replace('aws-cli/', '')
                    else:
                        version = version_output.split()[0] if version_output else 'installed'
                    print(f"   ✓ {tool}: {version}")
                elif tool == 'node':
                    # Node version format: "v18.17.0"
                    version = version_output.replace('v', '') if version_output.startswith('v') else version_output
                    print(f"   ✓ {tool}: {version}")
                else:
                    print(f"   ✓ {tool}: {version_output.split()[0] if version_output else 'installed'}")
            else:
                print(f"   {tool}: not found (exit code {result.returncode})")
                if result.stderr:
                    print(f"      Error: {result.stderr.strip()}")
                all_good = False
        except subprocess.TimeoutExpired:
            print(f"   {tool}: command timeout")
            all_good = False
        except FileNotFoundError:
            print(f"   {tool}: command not found")
            all_good = False
        except Exception as e:
            print(f"   {tool}: error checking version ({str(e)})")
            all_good = False
    
    # Special check for CDK
    cdk_found, cdk_version, cdk_command = check_cdk_specifically()
    if cdk_found:
        print(f"   cdk: {cdk_version} (via {cdk_command})")
    else:
        print(f"   cdk: not found")
        print(f"      Try: npm install -g aws-cdk")
        all_good = False
    
    return all_good

def main():
    """Run all pre-deployment checks"""
    print("Pre-Deployment Checks for Certification Coupon Hunter")
    print("=" * 60)
    
    # Load environment
    env_vars = load_env()
    
    # Run checks
    checks = [
        check_required_tools(),
        check_aws_credentials(),
        check_bedrock_access(),
        check_cdk_bootstrap(),
        check_existing_stacks()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 60)
    print(f"Pre-deployment Check Results: {passed}/{total} passed")
    
    if passed == total:
        print("All checks passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Run: make deploy")
        print("2. Or run: ./deploy.sh")
        return True
    else:
        print("⚠️  Some checks failed. Please fix the issues above before deploying.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Checks interrupted")
        sys.exit(1)