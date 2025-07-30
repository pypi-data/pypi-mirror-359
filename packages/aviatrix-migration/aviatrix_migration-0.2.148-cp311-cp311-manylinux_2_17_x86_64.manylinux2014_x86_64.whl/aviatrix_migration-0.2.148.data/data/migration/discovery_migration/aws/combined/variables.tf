variable "controller_ip" {}
variable "aws_account" {}
variable "aws_account_role" {}
variable "aws_ctrl_account" {}
variable "ctrl_role_app" {}
variable "ctrl_role_ec2" {}
variable "gateway_role_app" {}
variable "gateway_role_ec2" {}
{% if data.tf_controller_access.ssm_role %}
variable "ssm_role" {}
{% endif %}
{% if data.configure_spoke_gw_hs %}
variable "deploy_2_spokes_only" {
  type = bool
  default = false
}
variable "deploy_dummy_spokes" {
  type    = bool
  default = false
}
{% endif %}