# Design and clinical boundaries

## Product contract

Fluent supports communication opportunities; it does not try to make an autistic
child appear less autistic. A person's communication is valuable regardless of
speech fluency, pronunciation, use of AAC, or participation in an activity.

The primary experience is a communication board, not a test. Speech is optional.
No child data is used to train a model. No dataset supplied in the original
repository establishes therapeutic effectiveness.

## Interaction decisions

* Label every symbol in text. Symbols are original general-purpose line drawings,
  not a standardized or clinically validated symbol set.
* Keep no, stop, help, and a break reachable in each category. Reduce visible
  choices without removing vocabulary.
* Use predictable navigation and native buttons, labels, selects, and a dialog.
  Include a skip link, visible focus, status announcements, and explicit errors.
* Give the child control of audio. Do not play sound on startup or card taps.
  Cancel playback when pausing, changing sections, or hiding the page.
* Avoid flashing, animation, timers, countdowns, streaks, prizes for compliance,
  negative feedback, and forced repetition.
* Offer large text and device/light/dark appearance. Use a single accent and
  neutral surfaces. Do not encode category meaning only through color.
* Start without collecting data. Use caregiver opt-in for stored observations
  and make revocation and deletion real operations, not just hidden UI.

These are implementation intentions, not evidence of accessibility conformance.
Screen-reader, switch, eye-gaze, motor-access, language, sensory, and child
usability evaluation remain necessary with intended users.

## Observations are not outcomes

Saved counts mean a caregiver recorded events. They do not establish speech
accuracy, learning, engagement, intelligence, diagnosis, or clinical improvement.
Listening and skipping are first-class options, not failed attempts.

Comfort must be shared by the child, not inferred by the app. No emotion
recognition or behavioral compliance model is present. The app does not decide
what a person needs from facial expressions or voice.

## Professional context

The following public resources inform the broad communication-support boundary.
They do not endorse Fluent, validate its activities, or establish that its
particular implementation is effective.

* [ASHA public AAC information](https://www.asha.org/public/speech/disorders/aac/)
  redirects to Helping You Communicate. It describes AAC as multimodal,
  individualized support and the role of speech-language professionals in
  assessment, customization, and access methods.
* [Communication Bill of Rights](https://www.asha.org/njc/communication-bill-of-rights/)
  is a professional reference for communication rights; review it with the
  people designing and using any AAC support.
* [NHS help and support for autistic people and families](https://www.nhs.uk/conditions/autism/help-and-support/)
  describes routes to local and community support in the UK.

## Before public or clinical use

Required work includes professional content review, autistic-led co-design,
individual access assessment, age-appropriate safeguarding, legally appropriate
consent/assent, retention policy, privacy and threat assessment, independent
accessibility evaluation, prospective usability work, and appropriate clinical
and regulatory review.

Public hosting would also require genuine authentication, authorization,
TLS, secure operational processes, and a deployment design that does not rely
on loopback restrictions. This branch deliberately does not offer that mode.
