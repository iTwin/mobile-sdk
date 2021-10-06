Pod::Spec.new do |spec|
  spec.name         = "itwin-mobile-sdk"
  spec.version      = "0.0.29"
  spec.summary      = "iTwin Mobile SDK"
  spec.homepage     = "https://github.com/iTwin/mobile-sdk"
  spec.license      = { :type => "MIT", :file => "LICENSE.md" }
  spec.author       = "Bentley Systems Inc."
  spec.platform     = :ios
  spec.source       = { :git => "#{spec.homepage}.git", :tag => "#{spec.version}"}
  spec.source_files = "Sources/**/*"
  spec.swift_versions = "5.3"
  spec.ios.deployment_target = "12.2"
  spec.pod_target_xcconfig = { 'ENABLE_BITCODE' => 'NO' }
  spec.pod_target_xcconfig = { 'ONLY_ACTIVE_ARCH' => 'YES' }
  spec.user_target_xcconfig = { 'ONLY_ACTIVE_ARCH' => 'YES' } # not recommended but `pod lib lint` fails without it
  spec.dependency "PromiseKit", "~> 6.8"
  spec.dependency "PromiseKit/CoreLocation", "~> 6.0"
  spec.dependency "PromiseKit/Foundation", "~> 6.0"
  spec.dependency "ReachabilitySwift"
  spec.dependency "itwin-mobile-ios-package", "~> 2.19.18"
end
