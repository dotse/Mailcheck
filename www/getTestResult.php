<?php

require_once dirname(__FILE__) . '/../include/common.php';
require_once dirname(__FILE__) . '/../include/tests.php';

header('Content-Type: application/json; charset=utf-8');

// Both of these must be set
if (isset($_GET['test']) == false || isset($_GET['time']) == false)
{
	echo json_encode(array('state' => 'NOT_FOUND', 'test_id' => 0));
}

// Find out if we are trying to access a normal or secret url
$isSecretURL = false;
$time = intval($_GET['time']);
if ($time > 0)
{ // normal url
	$column = 'id';
	$testId = intval($_GET['test']);
}
else 
{ 
	// secret url
	$column = 'sid';
	$testId = sanitize_hash($_GET['test']);
	$isSecretURL = true;
}

$last_result = isset($_GET['last_result']) ? intval($_GET['last_result']) : 0;

//
// Get results from a running test, if it's running
//
$sql = 'SELECT *,extract(EPOCH from queued)::integer as start_time FROM test WHERE (id = $1 OR parent = $1) AND extract(EPOCH from queued)::integer = $2';
$testData = Database::query($sql, array($testId, $time));
if (is_array($testData))
{
	$testData = array_shift($testData);

	$child = Database::query("SELECT id FROM test WHERE parent = $1", array($testId));
	$childId = null;
	if (is_array($child))
		$childId = $child[0]['id'];

	if ($childId != null)
	{
		$where = 'test_id IN ($1, $2)';
		$param = array($testId, $childId);
	}
	else
	{
		$where = 'test_id = $1';
		$param = array($testId);
	}

	$sql_plugins = 'SELECT * FROM plugin WHERE ' . $where .' ORDER BY id ASC';
	$result = Database::query($sql_plugins, $param);
	$pluginInformation = array();
	if (is_array($result))
	{
		foreach ($result as $row)
			$pluginInformation[$row['plugin']] = array('status' => $row['status'], 'category' => $row['category']);
	}

	$params = array($last_result);
	$params = array_merge($param, $params);
	$sql = 'SELECT * FROM plugin_result WHERE ' .$where.' AND id > $'.count($params).' ORDER BY id ASC';
	$result = Database::query($sql, $params);
	if (is_array($result) == false)
		$result = array();
	
	// group by tables first
	$plugins = array();
	foreach ($result as $row)
	{
		$plugin = $row['plugin'];
		if (isset($plugins[$plugin]) == false)
			$plugins[$plugin] = array();

		$key = 'table_id';
		if ($row['child_table_id'] != null)
			$key = 'child_table_id';

		if (isset($pluginInformation[$plugin]))
		{
			$row['plugin_status'] = $pluginInformation[$plugin]['status'];
			$row['category'] = $pluginInformation[$plugin]['category'];
		}

		if (isset($plugins[$plugin][$row[$key]]) == false)
			$plugins[$plugin][$row[$key]] = array();

		$plugins[$plugin][$row[$key]][] = $row;
	}	

	// Compile output text
	$id = 0;
	$finalOutput = array('data' => array());
	$goldCount = 0;
	foreach ($plugins as $plugin => $data)
	{
		$pluginData = array('data' => array(), 'status' => 838);

		ksort($data); // TODO: i dont know if this will be correct all the time
		foreach ($data as $table)
		{
			$output = array('status' => 0);
			foreach ($table as $row)
			{
				if ($row['extra'] != null || $row['extra'] != '')
					$output['type'] = $row['extra'];

				if ($row['name'] == 'output_text' )
				{
					$output['message'] = $row['value_text'];
					$output['status'] = $row['value_numeric'];
				}
				else if ($row['name'] == 'goldstar')
				{
					$output['message'] = $row['value_text'];
					$goldCount += intval($row['value_numeric']);
					$output['gold'] = intval($row['value_numeric']);
				}
				else if ($row['name'] == 'param')
				{
					if (isset($output['params']) == false)
						$output['params'] = array();
					$output['params'][] = $row['value_text'];
				}
			}
			$id = $row['id'];

			if (isset($output['message']))
			{
				if ($output['status'] <= -1)
					$message = nl2br((translate($output['message'], isset($output['params']) ? $output['params'] : null)));
				else
					$message = nl2br(htmlentities(translate($output['message'], isset($output['params']) ? $output['params'] : null), ENT_COMPAT, 'UTF-8'));
			}
			else
				$message = '';

			$a = array(
				'message' => $message,
				'status' => $output['status'],
			);
			unset($output['message'], $output['params'], $output['status']);
			$pluginData['data'][] = array_merge($a, $output);

			if (isset($row['plugin_status']) == false)
				continue;

			$pluginData['status'] = $row['plugin_status'];
			$category = $row['category'];

			if (isset($finalOutput['data'][$category]) == false)
				$finalOutput['data'][$category] = array('data' => array(), 'status' => 0);

			$finalOutput['data'][$category]['data'][$plugin] = $pluginData;
			$finalOutput['data'][$category]['data'][$plugin]['plugin'] = translate($plugin);
			$finalOutput['data'][$category]['category'] = translate($category);

			if ($row['plugin_status'] > $finalOutput['data'][$category]['status'])
				$finalOutput['data'][$category]['status'] = $row['plugin_status'];
		}
	}

	$finalOutput['time'] = $testData['start_time'];
	$finalOutput['last_result'] = $id;
	$finalOutput['status'] = $testData['status'];
	$finalOutput['state'] = 'RUNNING';
	$finalOutput['gold'] = $goldCount;
	$finalOutput['domain'] = $testData['domain'];

	if ($testData['fast_finished'] !== null)
		$finalOutput['state'] = 'SLOW_FINISHED';
	if ($testData['finished'] !== null)
	{
		$finalOutput['state'] = 'FINISHED';
		$finalOutput['finished'] = substr($testData['finished'], 0, 19);
	}
	
	// If the test isn't finished, get the latest live feedback row and send it back
	if ($finalOutput['state'] != 'FINISHED')
	{
		$feedback = Database::query('SELECT message,arg0,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9
			FROM live_feedback WHERE test_id = $1 ORDER BY created DESC LIMIT 1', array($testId));
		if (is_array($feedback))
		{
			$feedback = $feedback[0];

			$params = array();
			for ($i=0; $i < 10; $i++)
			{
				if ($feedback['arg' . $i] != null && $feedback['arg' . $i] != '')
					$params[] = translate($feedback['arg' . $i]);
			}
			$finalOutput['message'] = translate($feedback['message'], $params);
		}
	}

	//echo "<pre>"; var_dump($finalOutput); die;
	echo json_encode($finalOutput);
	die;
}


//
// Test queued?
//
$sql = 'SELECT domain, test_id, extract(EPOCH from start_time)::integer as start_time FROM queue WHERE test_id = $1 AND extract(EPOCH from start_time)::integer = $2 LIMIT 1';
$queue = Database::query($sql, array($testId, $time));
if (is_array($queue))
{
	$queue = $queue[0];
	echo json_encode(array('state' => 'QUEUED', 'test_id' => $testId, 'time' => $queue['start_time'], 'domain' => $queue['domain']));
	die;
}

 
//
// If nothing else fits, test doesn't exist
//
echo json_encode(array('state' => 'NOT_FOUND', 'test_id' => $testId));
die;

?>
