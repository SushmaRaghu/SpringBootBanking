import json
import re

def update_dockerfile_version(json_file, docker_file):
    # Load JSON data
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Read the original Dockerfile content
    with open(docker_file, 'r') as dockerfile:
        dockerfile_content = dockerfile.read()

    # Store the updated Dockerfile content (initially it's just the original content)
    updated_dockerfile_content = dockerfile_content

    # Iterate through changes in the JSON
    for pr in data['pull_requests']:
        for change in pr['changes']:
            # If the package type is 'os', we need to update the Dockerfile
            if change['package_type'] == 'os':
                package = change['package']
                current_version = change['current_version']
                upgrade_version = change['upgrade_version']

                print(f"Processing Docker package: {package}, Current version: {current_version}, Upgrade version: {upgrade_version}")

                # Regex to find the image name and current version in the Dockerfile's FROM line
                from_line_pattern = re.compile(r"^FROM\s+" + re.escape(package) + r":([^\s]+)", re.MULTILINE)
                match = from_line_pattern.search(dockerfile_content)

                if match:
                    # Extract the current version from the match and compare it
                    current_image_version = match.group(1)

                    if current_image_version == current_version:
                        # Update the Dockerfile with the upgrade version
                        updated_dockerfile_content = dockerfile_content.replace(current_image_version, upgrade_version)
                        print(f"Updated Dockerfile: {package}:{current_image_version} to {upgrade_version}")
                    else:
                        print(f"Version mismatch: Dockerfile has {current_image_version} but JSON has {current_version}")
                else:
                    print(f"Image {package} not found in Dockerfile.")

    # Output the updated Dockerfile to the console
    print("\nUpdated Dockerfile:\n")
    print(updated_dockerfile_content)

    # Write the updated Dockerfile back to the file
    with open(docker_file, 'w') as dockerfile:
        dockerfile.write(updated_dockerfile_content)
    print(f"\nDockerfile updated successfully!")

 

# Example usage:
update_dockerfile_version('<path to json which has what image to be upgraded>', 'path to Dockerfile')
