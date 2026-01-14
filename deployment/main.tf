resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow devices to SSH into the machine."

  tags = {
    Name = "VPC security group for SSH access."
  }
}

resource "aws_vpc_security_group_ingress_rule" "allow_all_traffic_ssh" {
  security_group_id = aws_security_group.allow_ssh.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = "22"
  to_port           = "22"
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.allow_ssh.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # all ports
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv6" {
  security_group_id = aws_security_group.allow_ssh.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" # all ports
}

data "aws_ebs_volume" "skill_llm" {
  most_recent = true
  filter {
    name   = "tag:Name"
    values = ["skill-llm"]
  }
}

resource "aws_instance" "test_spot" {
  availability_zone = data.aws_ebs_volume.skill_llm.availability_zone
  ami           = "ami-07b531d2a90722369"
  instance_type = var.instance_type
  key_name      = "skill-llm"
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  instance_market_options {
    market_type = "spot"
    spot_options {
      instance_interruption_behavior = "stop"
      spot_instance_type = "persistent"
    }
  }

  root_block_device {
    volume_size = 100
    volume_type = "gp3"
  }
  tags = {
    Name = "LLM Training Spot Instance"
  }

  user_data = <<-EOF
      #!/bin/bash

      # Install necessary packages
      apt install python3-pip -y

      # Create the mount directory
      mkdir -p /home/ubuntu/dev
    
      # Wait for the device to be attached
      while [ ! -e /dev/nvme1n1 ]; do sleep 1; done
      
      # Create a file system on the volume (xfs is recommended for AWS)
      # The '-f' forces the overwrite if the disk was previously formatted
      mkfs -t xfs /dev/nvme1n1

      # Mount the volume
      mount /dev/nvme1n1 /home/ubuntu/dev

      # Get the UUID of the device to ensure persistent mounting across reboots
      UUID=$(blkid -s UUID -o value /dev/nvme1n1)

      # Add entry to fstab for auto-mount on reboot
      # echo "UUID=$UUID  /home/dev  xfs  defaults,nofail  0  2" >> /etc/fstab
    
      # Adjust permissions so the default user can access it (optional)
      chown -R ubuntu:ubuntu /home/ubuntu/dev
      chmod 755 /home/ubuntu/dev

      cd /home/ubuntu/dev
      ### Uncomment the lines below if fresh environment setup is needed ###
      # git clone https://github.com/luvellieee/Thesis-2.git thesis
      # chmod 744 thesis
      cd thesis
      touch installation_log.txt
      chown ubuntu:ubuntu installation_log.txt
      chmod 644 installation_log.txt

      ##############################
      # Set up the virtual environment and install dependencies
      ##############################
      su ubuntu
      ### Uncomment the lines below if fresh environment setup is needed ###
      # mkdir .venv
      # python3 -m venv .venv
      # echo "" > installation_log.txt
      # pip install -r Skill-Extraction/requirements.txt --log installation_log.txt
    EOF
}

resource "aws_volume_attachment" "ebs_att" {
  device_name = "/dev/sdh"
  volume_id   = data.aws_ebs_volume.skill_llm.id
  instance_id = aws_instance.test_spot.id
}

output "public_ip" {
  value = aws_instance.test_spot.public_ip
}
