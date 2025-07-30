# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'v0.2.2'
BUILD_TIME = '2025-07-01T19:56:20Z'
BUILD_COMMIT = '64be671454337b48e46e7dd6d52214ffed069337'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
