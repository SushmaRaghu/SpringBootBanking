import json
import xml.etree.ElementTree as ET

def update_pom_version(json_file, pom_file):
    # Load the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Load and parse the pom.xml file
    tree = ET.parse(pom_file)
    root = tree.getroot()

    # Define the namespace (for handling XML tags correctly)
    namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}

    # Iterate through each pull request's changes
    for pr in data['pull_requests']:
        for change in pr['changes']:
            # If the package type is not 'os', we need to update the pom.xml
            if change['package_type'] != 'os':
                package = change['package']
                current_version = change['current_version']
                upgrade_version = change['upgrade_version']

                print(f"Processing Maven package: {package}, current_version: {current_version}, upgrade_version: {upgrade_version}")

                # Split the package into groupId and artifactId
                if ":" not in package:
                    print(f"Skipping invalid package format: {package}")
                    continue

                groupId, artifactId = package.split(":", 1)

                # Find the matching dependency in pom.xml
                dependency = root.find(f".//maven:dependencies/maven:dependency[maven:groupId='{groupId}'][maven:artifactId='{artifactId}']", namespace)

                if dependency is not None:
                    # Check if the current version matches the version in pom.xml
                    version_element = dependency.find('maven:version', namespace)

                    if version_element is not None and version_element.text == current_version:
                        # Update the version with the upgrade_version
                        version_element.text = upgrade_version
                        print(f"Updated {groupId}:{artifactId} from {current_version} to {upgrade_version} in pom.xml.")
                    else:
                        print(f"No matching version for {groupId}:{artifactId} or version mismatch in pom.xml.")
                else:
                    print(f"Dependency {groupId}:{artifactId} not found in pom.xml.")

    # Output the updated pom.xml to the console
    updated_xml_str = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
    print("\nUpdated pom.xml:\n")
    print(updated_xml_str)

    # Write the updated pom.xml back to the file
    tree.write(pom_file, xml_declaration=True, encoding='UTF-8')
    print(f"\npom.xml updated successfully!")

 
 

# Example usage:
update_pom_version('<path to json which has what package needs to be upgraded>', 'path for pom.xml')
