<?php
require_once '../include/common.php';

$r = Request::getCurrentRequest();
$output	 		= array('data' => array());
$domain			= $r->GET('domain', 'url');
$time			= intval($r->GET('time', 'int'));
$currentPage	= intval($r->GET('page', 'int', 1));
$test			= $time == 0 ? $r->GET('test', 'hash') : intval($r->GET('test', 'int'));

$where			= $time == 0 ? 'sid != ?' : 'id != ?';
$params			= array($domain, $test);


$pageSize = Config::get('HISTORY_PAGE_SIZE');
$totalPages = 1;
// Get the highest status 
//$sql = '(SELECT max(r.status) FROM result r WHERE r.test_id = t.id AND r.status in (1,2,3) )';

/*$result = Database::query('SELECT *, ' . $sql .' as finalstatus, extract(EPOCH from t.queued)::integer as start_time
	FROM test t WHERE t.domain = ? AND ' . $where .' AND t.ended IS NOT NULL AND t.public = 1 ORDER BY t.started DESC OFFSET ' . (($currentPage-1)*$pageSize) . ' LIMIT ' . $pageSize,
	$params);*/
$result = Database::query('SELECT *,extract(EPOCH from queued)::integer as start_time FROM test WHERE domain = ? AND '.$where.' AND finished IS NOT NULL AND parent IS NULL ORDER BY started DESC OFFSET ' . (($currentPage-1)*$pageSize) . ' LIMIT ' . $pageSize, $params);
if (is_array($result))
{
	foreach ($result as $row)
	{
		$output['data'][] = array(
			'started' => substr($row['started'], 0, 19),
			'domain' => $row['domain'],
			'className' => statusToClass($row['status']),
			'url' => 'http://' . $_SERVER['SERVER_NAME'] . '/result/' . $row['start_time'] . '-' . $row['id'],
			);
	}

	$total = Database::query('SELECT count(id) as total FROM test WHERE domain = ? AND ' . $where .' AND finished IS NOT NULL AND public = 1', $params);
	$totalPages = is_array($total) ? $total[0]['total'] : 0;
}

$output['current_page'] = $currentPage;
$output['pages'] = intval(ceil($totalPages / $pageSize));
header('Content-type: application/json');
echo json_encode($output);
?>
