# Imou Life Integration

A Home Assistant custom integration that connects to the Imou cloud API to monitor and control Imou hardware devices (cameras and other smart home products).

## Language

### Devices

**Device**:
A physical Imou hardware unit registered to an Imou Account. May expose any combination of Capabilities.
_Avoid_: Camera (too narrow — not all Devices have a camera)

**Battery-Powered Device**:
A Device that runs on battery and sleeps between polls to conserve power. Requires a dedicated polling strategy.
_Avoid_: Battery device, sleep device

**Mains-Powered Device**:
A Device with a permanent power supply that remains continuously reachable.
_Avoid_: Wired device, always-on device

**Offline Device**:
A Device that exists in the Imou Account but is temporarily unreachable due to an unexpected condition (e.g., power cut, network failure).
_Avoid_: Unavailable device, disconnected device

**Stale Device**:
A Device that Home Assistant has a config entry for but that no longer exists in the Imou Account — removed, physically replaced, or the account changed. Distinct from an Offline Device.
_Avoid_: Missing device, deleted device, orphaned device

### Capabilities

**Capability**:
A single addressable feature of a Device that becomes a Home Assistant entity — e.g., motion detection, night vision mode, camera stream, siren, push notifications.
_Avoid_: Sensor (too narrow), sensor_instance (implementation artifact), feature (overloaded)

**Push Notification**:
A Capability that, when enabled, causes Imou to proactively call Home Assistant with device events (e.g., motion detected) in near real-time. Requires a publicly accessible Home Assistant instance.
_Avoid_: Event callback, webhook, push alert

### Imou Account

**Imou Account**:
The authenticated identity that owns Devices and gates access to the Imou cloud API, identified by an App ID and App Secret pair.
_Avoid_: Credentials, developer account, API keys

### Device Lifecycle

**Discovery**:
The automatic periodic scan of the Imou Account that detects Devices not yet configured in Home Assistant, triggering a confirmation flow for each one found.
_Avoid_: Auto-discovery, device scan

**Manual Registration**:
The one-shot process of adding a Device to Home Assistant by providing its Device ID directly, bypassing Discovery.
_Avoid_: Manual discovery, manual setup

### Battery-Powered Device States

**Sleep**:
A state in which a Battery-Powered Device is intentionally unreachable — entered automatically based on a Sleep Schedule, low battery level, or explicit command. Distinct from being Offline.
_Avoid_: Sleeping, hibernation, standby

**Battery Optimization**:
A behavioral adjustment applied to a Battery-Powered Device when its battery drops below the Battery Threshold: Capabilities are dialed back (reduced motion sensitivity, lower recording quality, LEDs off) while the Device remains reachable.
_Avoid_: Power saving, battery saver

**Sleep Schedule**:
A time-based rule that determines when a Battery-Powered Device should enter and exit Sleep.
_Avoid_: Sleep timer, sleep window

**Battery Threshold**:
The battery level percentage at which Battery Optimization activates automatically.
_Avoid_: Low battery limit, optimization trigger

**Power Mode**:
A preset configuration (balanced, performance, power-saving) that determines how aggressively a Battery-Powered Device conserves power during normal operation.
_Avoid_: Power profile, energy mode

## Relationships

- A **Device** exposes one or more **Capabilities**
- A **Battery-Powered Device** and a **Mains-Powered Device** are both **Devices**, distinguished by power source
- An **Offline Device** is unreachable due to an unexpected condition; it still exists in the **Imou Account**
- A **Stale Device** no longer exists in the **Imou Account** at all
- A **Battery-Powered Device** in **Sleep** is unreachable by design — this is not the same as being **Offline**
- **Battery Optimization** and **Sleep** are independent states: a Device can be Battery-Optimized while reachable, and can Sleep without Battery Optimization active
- **Discovery** finds new Devices automatically; **Manual Registration** is the deliberate one-shot alternative
- **Push Notification** is a **Capability**; enabling it registers a callback URL with the **Imou Account**

## Example dialogue

> **Dev:** "A user reported their camera shows as unavailable — is it Offline or Stale?"
> **Domain expert:** "Check whether the Device still appears in the Imou Account. If it does and is just unreachable, it's **Offline**. If it's gone from the account entirely, it's **Stale** — HA has a config entry for something that no longer exists."

> **Dev:** "What about a battery doorbell that's not responding at 2 AM — is that Offline?"
> **Domain expert:** "Not necessarily. If it has a Sleep Schedule covering that window, it's in **Sleep** — unreachable by design. Check the schedule before calling it Offline."

> **Dev:** "The user enabled 'push notifications' on their device — what Capability does that map to?"
> **Domain expert:** "That's the **Push Notification** Capability. When it's on, Imou calls back to HA when events happen. Make sure their HA instance has a public URL configured, otherwise Imou can't reach it."

> **Dev:** "We found a new device on the account during the background scan — how does it get added?"
> **Domain expert:** "That's **Discovery**. It periodically scans the **Imou Account** for unconfigured Devices and surfaces them for confirmation. If the user already knows the device ID and wants to add it directly, that's **Manual Registration** instead."

## Flagged ambiguities

- `sensor_instance` in the codebase refers to any **Capability**, not just sensors — this is a misnomer to address over time
- "alarm" appears in two unrelated places: `motionAlarm` (a binary sensor Capability for motion state) and the Siren Capability (a physical audio alarm) — these are distinct and should not be conflated
