SELECT DISTINCT
sl.id session_id,
act.action_name,
sl.ts_created,
sl.useraccount_id,
sl.subject_id,
ft.display_name,
ft.section,
ft.topic,
ft.state_id,
atv.video_id
FROM ActionTracking as act
INNER JOIN ActionTrackingVideo as atv on act.id = atv.action_tracking_id
INNER JOIN FolderTree as ft on atv.video_id = ft.id
INNER JOIN SessionLog as sl on sl.id = act.session_log_id
WHERE sl.subject_id = 1
AND sl.ts_created BETWEEN '2019-06-15' AND '2019-07-01'
AND act.action_name = 'video_play';
