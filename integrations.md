# Production integration contracts

## ERP/LMS/timetable
Expose a read-only adapter that returns `studentId`, `courseId`, `roomId`, `startsAt`, and `endsAt`. Keep source IDs separate from campus entity IDs. Sync failures must leave the last verified timetable available.

## Live room availability
Only publish `available`, `occupied`, or `unknown` with `source`, `validUntil`, and consent/policy metadata. Never infer occupancy from personal location data.

## Emergency/security
Replace demo buttons with an approved security desk API and verified emergency plan. Keep emergency content available without sign-in and show an explicit stale-data timestamp.

## Authentication
Replace demo tokens with the university identity provider. Enforce roles in the API, never only in the browser. Use institution-approved contact methods and retain audit records for all writes.
