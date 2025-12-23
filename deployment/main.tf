# Request a spot instance at $0.03
resource "aws_spot_instance_request" "llm_trainer" {
  ami           = "ami-07b531d2a90722369"
  instance_type = "g6e.xlarge"
  spot_type     = "persistent"
  instance_interruption_behavior = "stop"

  tags = {
    Name = "LLMTraining"
  }
}
