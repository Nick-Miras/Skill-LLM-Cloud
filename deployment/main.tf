resource "aws_instance" "test_spot" {
  ami           = "ami-07b531d2a90722369"
  instance_type = var.instance_type
  key_name      = "llm-trainer"

  instance_market_options {
    market_type = "spot"
    spot_options {
      instance_interruption_behavior = "stop"
      spot_instance_type = "persistent"
    }
  }

  root_block_device {
    volume_size = "150"
  }
  tags = {
    Name = "test-spot"
  }
}
