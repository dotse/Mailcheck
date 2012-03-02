<?php

require_once dirname(__FILE__) . '/../config/config.php';

/**
 * Helper class that handles connection to the database.
 */
class Database
{
	private static $_connection = null;
	
	/**
	 * @TODO remove hardcoded stuff
	 */
	public static function connect()
	{
		if (self::$_connection !== null)
			return true;
		$host = Config::get('database', 'host');
		$db = Config::get('database', 'database');
		$uname = Config::get('database', 'username');
		$pword = Config::get('database', 'password');
		self::$_connection = @pg_connect("host=$host dbname=$db user=$uname password=$pword");
	}
	
	/**
	 * Query the database for some information. Note: use ? to the mark the position of params.
	 *
	 * query('select * from mytable where id = ?', array(12));
	 *
	 * @param string $sql		Sql query string.
	 * @param array $params		Optional. Array with params used in the sql query.
	 * @return bool|array		Array with data if available, true if successfull but no data returned,
	 * 							and false if query failed.
	 */
	public static function query($sql, $params=array())
	{
		if (self::$_connection === null)
			self::connect();
			
		// Change all ? to $x so that pg_query_params is happy
		$i = 0;
		while (($pos = strpos($sql, '?')) !== false)
		{
			$i++;
			$sql = substr_replace($sql, '$'.$i, $pos, 1);
		}
		
		$result = pg_query_params(self::$_connection, $sql, $params);
		
		if ($result === false)
			return false;
			
		$numRows = pg_num_rows($result);
		if ($numRows == 0)
			return true;
			
		$data = array();
		while ($row = pg_fetch_assoc($result))
			$data[] = $row;
			
		return $data;
	}
}