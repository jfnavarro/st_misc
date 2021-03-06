#!/bin/sh

# By running this script on a newly create EC2 instance, Joel, Daire, Henrik and Erik are given root access to the instance.

echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqPp5J8wsmqiAs+lBcnp+z0rdKfp+boranzTRew9++GUZtzQE48pfjyZPMe16q5AbSALvxz+L/clrsYSqUKVT/W28p3Druf0Z5l4kKv76d0kMq4a9qLcvCBwE/CcDdd7Jrzi7jyG6oHkB84ZoeyZOXAnfB+L/IjS8k2OoF+1pjcgSl1zrDLY2VJLt+Z40BcXIahdvwT0DCHjJIsstzX5sJTxOyJSYMnIuW+1srtDzWzOy6ZLd6Z1DTO6OcO/wA3I8greiuvXwfDGXSW5skPorYMG3Ou0pOipJMvcwkK7EFlqrvpebH7P5QAQmqYWlR+xBR8HwRoqyqPhGBdTc7TFdx spatial
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCpM9UmgHHTfAP4T90MTeZn1B8NzCdednfzo2MGSEGLsh14jZy6J79q+qHjOcqF0UsMI+HbMc9Sfd/SkhEq5Jtt2TPTex8sS+j3Gg4mD7vRR0O8p7T7ddZJw1jFyPw4fEp1jnMf75O2RznKIfkcQ88LROyuhDGK8eWukia2ExAt8WdYOsgJGWGUeZaSf6Kb6Fc+EaiHJyM41l1smgdJ7ckZY32wpLQ6O2LZ9dyeuKWWnLI3JVt9rRQ3354K/GlVyPjNjhSxFcgXJ7rS7Z8yHpqkmFQqvWc/KTAk/i+ZbnZNOS+u+h+z6H5Ojgdwtt+QOt3dDsxnfasB8u56NNXSgI/d joelsjostrand@130-229-10-186-dhcp.wlan.ki.se
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDj50udxHublerV9qCbpp/VkJPhUi00HIHhqBV4JsWTGTmmq/Z/rrLEMvccyeEbaTwJDpE8qoYkGZ+q9NZsDbQTeUe8QrxK2EeEqoQyia6rDch6aJkIYAJzbeZYkgpx7Hoic/ZK0J1ivSJKdsTmyVm+DQpyXd51pyvEIHm3WZWSQXTEBG2wkA72aIH2Ct0jlDdAGcL55aP2+umbMs7WWVYuwt5KsbXWcD5Nj7J2I1Tla+j6Kb2GriDaig7fxUhB8idG9fbGygRSeggqzCfS2cVyGIY8zmfXDV1dE1bOODPy8hdoCeAP0y9euQ3lZggUqPafJ+Vel7JuZMgJ3hz/Q4G1 esjolund@linux
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8tRmjIOKsqBz9H6/DQjcY2CFdLbifnmW7IcN257u7ltDxZWP27NzruPf3yLz/4y4q/zeE6l9gDX18NusmhG82jzx9qDS3Agl1bJEt10D171vGLO7IGvYT+jPodTo7mv1NQxwaZEBzDPb54QDzVXTzmrzWreqKQNyZluhJJeSfOkhZ02bA0qT5AoqrvWC+FB+Q+2x022y8kJixYkL1uTf6PV9WDpFHqrc1HKqy4oD/UIwgK3kxMQmqHGrZbErZI5DWgyog6WW6EFNEHU200uMrTIP8S4dWfE9/uokiOyvM0BxXO3jp/gBDhRsa7c4n7+Fm7PkO2IWoqQBTE8mC8NQf henriktreadup@HenrikTMBP.scilifelab.se
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDF+IF1Jk5P2um2rMvNqccnMPQqcfJkcimtxy/mDN1hOFQIh+TtBqS+AxycfvjOQwM1bYVWhzJvWLC5CKgdGhznK2sKRyLWKbilYFZuhOUDC91ZinhYqHnoWaBwqWEzEI59nNpjm8SJ4uHFnUzMBErsJOi1UWXoFd0Sz8fzn0NOx1TO+fqTir7KeiLSsxN2dDTcE3EyYcNbFlDzagCKY1O6P+upRZnorxuP6XZBhWr4GdeOivKZZzOiRjgCJgFx92YgN9yRsZEtEYUuLgBNFe3dusfFt9WN87r/Ldf0P9GroTO40Ojhpy99rP4IPaZ1S1Qu+k/ROcHnc8V5OkaJmBJpFencmBfZIJHCsWMmNAJwOA3NvGJiosdTyOz35A2EHAXRKoNvQtPsnkvWKhGxglBC7aQTUEH3HmklKV80O9+cSUhn5Tcdl96ACYktSIForaIF2Oi+9FFHY9EH6Xz27xLtsxVV7RWpvzxrJ8KnKN+ExoQrUWWLfM92/qEBOTzDRsqtRryrVlp4+GHAm49on9X7S3YX6xKMcpmVLWqmNTB+S3p1vbgZ1qoh9oPmEkufkxt/m18h5JeZ/cCTNy/NoSjo6zVobf7SOa/q/LqNQmxfJf6OT5I0D4f93YPR/UkkXSzZtJYUCTJRzPLyk6ZT4i7rw/r/FbmTta8UywzEj1ef9Q== daire.stockdale@scilifelab.se
" > /root/.ssh/authorized_keys

chmod 600 /root/.ssh/authorized_keys
chown root.root /root/.ssh/authorized_keys
#touch /root/user-data-was-here
