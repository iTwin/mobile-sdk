//---------------------------------------------------------------------------------------
//
//     $Source: FieldiOS/App/Utils/ITwinMobile.swift $
//
//  $Copyright: (c) 2020 Bentley Systems, Incorporated. All rights reserved. $
//
//---------------------------------------------------------------------------------------

import PromiseKit
import UIKit
import WebKit

// MARK: - Helper classes and extensions for converting the data that comes from WKWebView
class ITMDictionaryDecoder<T: Decodable> {
    static func decode(_ d: [String: Any]) throws -> T {
        let jsonData = try JSONSerialization.data(withJSONObject: d, options: .prettyPrinted)
        return try JSONDecoder().decode(T.self, from: jsonData)
    }
}


struct ITMRect: Codable, Equatable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

extension CGRect {
    init(_ alertRect: ITMRect) {
        // NOTE: Even though CGFloat is Float on 32-bit hardware, CGPoint and CGSize both have overridden initializers
        // that explicitly take Double.
        self.init(
            origin: CGPoint(x: alertRect.x, y: alertRect.y),
            size: CGSize(width: alertRect.width, height: alertRect.height)
        )
    }
}

// MARK: - ITwinMobile class

class ITwinMobile {
    private var components: [ITMComponent] = []
    init(viewController: UIViewController, wmuMessenger: ITMMessenger) {
        components.append(ITMActionSheet(viewController: viewController, wmuMessenger: wmuMessenger))
        components.append(ITMAlert(viewController: viewController, wmuMessenger: wmuMessenger))
//        components.append(ITMDatePicker(viewController: viewController, wmuMessenger: wmuMessenger))
    }

    func addComponent(_ component: ITMComponent) {
        components.append(component)
    }

    func detach() {
        for component in components {
            component.detach()
        }
    }
}

class ITMComponent: NSObject {
    var queryHandler: ITMQueryHandler?
    var wmuMessenger: ITMMessenger
    weak var viewController: UIViewController?

    init(viewController: UIViewController, wmuMessenger: ITMMessenger) {
        self.viewController = viewController
        self.wmuMessenger = wmuMessenger
        super.init()
    }

    func detach() {
        if let queryHandler = queryHandler {
            wmuMessenger.unregisterQueryHandler(queryHandler)
            self.queryHandler = nil
        }
    }
}
