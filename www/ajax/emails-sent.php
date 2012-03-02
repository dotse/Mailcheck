<?php

include_once '../../include/common.php';
include_once '../../include/tests.php';

$request = Request::getCurrentRequest();
$start_time = intval($request->POST('start_time', 'int'));
$test_id = intval($request->POST('test_id', 'int'));

//
// START A NEW TEST
//

$result = array();
Database::query("UPDATE queue SET waiting_input = $1 WHERE test_id = $2 AND extract(EPOCH FROM start_time)::integer = $3 RETURNING id", array('f', $test_id, $start_time));

$result = array(
	'state' => 'QUEUED',
	'test_id' => $test_id,
	'start_time' => $start_time,
	);

echo json_encode($result);
?>
