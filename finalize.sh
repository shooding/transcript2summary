#!/bin/bash
#
# A bash script to receive the directory of a newly published
# transcript and audio file.
#
# The first and only argument will always be the absolute path
# to the new directory.
#
# The path to a script needs to be given in:
# jigasi/jigasi-home/sip-communicator.properties

original_dir="$1"

# Generate a random simpler name for the symbolic link
simpler_name=$(mktemp -u /tmp/simpler_name_XXXXXX)

# Create the symbolic link
ln -s "$original_dir" "$simpler_name"

# Run the Docker command using the symbolic link because jigasi generates a hardtoguess folder name with many colons (cannot use with docker -v)
docker run --rm --network host --env-file .env -v "$simpler_name:/transcript_samples" shooding/transcript2summary /transcript_samples

# Remove the symbolic link after the Docker command completes
rm "$simpler_name"