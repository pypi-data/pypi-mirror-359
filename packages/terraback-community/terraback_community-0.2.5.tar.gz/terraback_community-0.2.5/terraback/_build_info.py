# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250701-2029'
BUILD_TIME = '2025-07-01T20:29:22Z'
BUILD_COMMIT = 'f5685c6b99c99aa204d4074204a4a2fe4edef906'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
