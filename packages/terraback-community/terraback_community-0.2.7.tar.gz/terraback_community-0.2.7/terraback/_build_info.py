# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250701-2034'
BUILD_TIME = '2025-07-01T20:34:51Z'
BUILD_COMMIT = 'ccfa08a14cb2cd6c44f250c9100f3b8c601930ee'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
