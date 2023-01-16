import boto3
import os
from flask import Flask, jsonify, request
from datetime import datetime

session = boto3.session.Session(
    aws_access_key_id=os.environ['ACCESS_KEY'],
    aws_secret_access_key=os.environ['SECRET_KEY'],
    region_name=os.environ['REGION']
)

app = Flask(__name__)

@app.route('/')
def get_asg_name():
    asgs = session.client('autoscaling')
    response = asgs.describe_auto_scaling_groups()
    all_asg = response['AutoScalingGroups']
    all_name = []
    for i in range(len(all_asg)):
        all_name.append(all_asg[i]["AutoScalingGroupName"])

    return all_name

@app.route('/updateasg')
def update_asg():
    name        = request.args.get('asg_name')
    ami_id      = ""
    lc_new_name = ""
    update_asg  = ""
    asgs        = session.client('autoscaling')
    response    = asgs.describe_auto_scaling_groups()
    all_asg     = response['AutoScalingGroups']

    for i in range(len(all_asg)):
        if all_asg[i]["AutoScalingGroupName"] == name:
            instance_id = all_asg[i]['Instances'][0]['InstanceId']
            ami_id      = create_ami(instance_id)
            lc_new_name = create_lc(all_asg[i]['LaunchConfigurationName'], ami_id)

            if lc_new_name != "":
                update_asg  = update_asg_for_new_lc(name, lc_new_name)
            break

    if lc_new_name != "" and update_asg["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {"result": "true", "LC": lc_new_name }

    return {"result": "false" }

def create_ami(instance_id):
    ami_name = datetime.now().strftime("%Y-%m-%d%H-%M-%S") + "-firegroup-ami"
    ec2 = session.client('ec2')
    ami_id = ec2.create_image(InstanceId=instance_id,Name=ami_name, NoReboot=True)
    return ami_id["ImageId"]

def create_lc(lc_name, ami_id):
    lcs = session.client('autoscaling')
    response = lcs.describe_launch_configurations()
    all_lc = response['LaunchConfigurations']
    for i in range(len(all_lc)):
        if all_lc[i]["LaunchConfigurationName"] == lc_name:
            lc_new_name     = datetime.now().strftime("%Y-%m-%d%H-%M-%S") + "-firegroup-lc"
            keypair         = all_lc[i]["KeyName"]
            instancetype    = all_lc[i]["InstanceType"]
            sg              = all_lc[i]["SecurityGroups"]
            userdata        = all_lc[i]["UserData"]
            instanceprofile = all_lc[i]["IamInstanceProfile"]
            lcs.create_launch_configuration(LaunchConfigurationName=lc_new_name,ImageId=ami_id,\
                     KeyName=keypair,SecurityGroups=sg,InstanceType=instancetype,IamInstanceProfile=instanceprofile,UserData=userdata)
            return lc_new_name

    return ""

def update_asg_for_new_lc(asg_name, lc_name):
    asg = session.client('autoscaling')
    response = asg.update_auto_scaling_group(AutoScalingGroupName=asg_name,LaunchConfigurationName=lc_name)
    return response

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
