# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = '0.2.0'
BUILD_TIME = '2025-07-01T18:46:45Z'
BUILD_COMMIT = 'e98de16cd8975131f35c1b5c3e85d01936e13e0f'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
