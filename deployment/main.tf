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

resource "aws_instance" "test_spot" {
  ami           = "ami-07b531d2a90722369"
  instance_type = var.instance_type
  key_name      = "llm-trainer"
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  instance_market_options {
    market_type = "spot"
    spot_options {
      instance_interruption_behavior = "stop"
      spot_instance_type = "persistent"
    }
  }

  root_block_device {
    volume_size = "50"
  }
  tags = {
    Name = "LLM Training Spot Instance"
  }
}

output "public_ip" {
  value = aws_instance.test_spot.public_ip
}
