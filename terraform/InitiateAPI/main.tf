resource "null_resource" "InitiateAPIGW" {
    provisioner "local-exec" {
        command = <<EOM
         python ${path.module}\deployswagger.py ${var.rest_api_name} ${var.swagger_file_name} ${var.aws_region}
        EOM
    }
}


