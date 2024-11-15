from lxml import etree
import json
import re
import subprocess

def update_pom_and_docker(json_file, pom_file, docker_file):
    # Load JSON data
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Read the original pom.xml content
    with open(pom_file, 'r') as pom:
        pom_content = pom.read()

    # Read the original Dockerfile content
    with open(docker_file, 'r') as dockerfile:
        dockerfile_content = dockerfile.read()

    # Initialize updated content for both files
    updated_pom_content = pom_content
    updated_dockerfile_content = dockerfile_content

    # Define XML namespace for pom.xml
    namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}

    # Process changes from the JSON for both pom.xml and Dockerfile
    for pr in data['pull_requests']:
        for change in pr['changes']:
            package = change['package']
            package_type = change['package_type']
            current_version = change['current_version']
            upgrade_version = change['upgrade_version']

            # If package_type is 'application', we need to update the pom.xml
            if package_type == 'application':
                groupId, artifactId = package.split(":")
                print(f"Processing POM package: {package}, Current version: {current_version}, Upgrade version: {upgrade_version}")
                
                # Convert the pom_content to bytes (to handle encoding correctly)
                pom_bytes = pom_content.encode('utf-8')
                
                # Parse the pom.xml using lxml from bytes
                root = etree.fromstring(pom_bytes, parser=etree.XMLParser(ns_clean=True))
                
                # Find the dependency in pom.xml using groupId and artifactId
                dependency = root.find(f".//maven:dependencies/maven:dependency[maven:groupId='{groupId}'][maven:artifactId='{artifactId}']", namespace)
                
                if dependency is not None:
                    # Find the version element and update it
                    version_elem = dependency.find('maven:version', namespace)
                    if version_elem is not None and version_elem.text == current_version:
                        version_elem.text = upgrade_version
                        print(f"Updated POM: {groupId}:{artifactId} {current_version} to {upgrade_version}")
                    else:
                        print(f"Version mismatch or version not found for {groupId}:{artifactId}.")
                else:
                    print(f"Dependency {groupId}:{artifactId} not found in pom.xml.")

                # Write the updated pom.xml content back to string
                updated_pom_content = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')

            # If package_type is 'os', we need to update the Dockerfile
            if package_type == 'os':
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

    # Write the updated pom.xml and Dockerfile back to the files
    with open(pom_file, 'w') as pom:
        pom.write(updated_pom_content)
    print(f"\nPOM.xml updated successfully!")

    with open(docker_file, 'w') as dockerfile:
        dockerfile.write(updated_dockerfile_content)
    print(f"\nDockerfile updated successfully!")

    # Run Git commands to commit and push changes
    subprocess.run(["git", "add", pom_file, docker_file])
    subprocess.run(["git", "commit", "-m", "Updated versions in pom.xml and Dockerfile based on update_info.json"])
    subprocess.run(["git", "push"])
    print("\nChanges committed and pushed to the repository.")

# Example usage:
update_pom_and_docker('./changes_mapper.json', './pom.xml', './Dockerfile')
