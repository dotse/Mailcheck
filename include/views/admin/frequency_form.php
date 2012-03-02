<?php
$edit = isset($_GET['edit']) ? 'edit' : 'new';
?>
<div class="breadcrumb">
	<a href="/admin">Admin</a> > <a href="/admin/frequency.php?list">Frequency list</a> > <?=ucfirst($edit)?>
</div>
<h4><?=ucfirst($edit)?> test frequency</h4>
<p>Set max tests and interval to 0 to blacklist the domain.</p>
<form method="post" action="/admin/frequency.php">
<div class="admin-form">
	<input type="hidden" name="id" value="<?=$this->row['id']?>" />
	
	<label>Domain</label>
	<div>
		<input type="text" name="domain" value="<?=$this->row['domain']?>" />
	</div>

	<label>Max tests</label>
	<div>
		<input type="text" name="max_tests" value="<?=$this->row['max_tests']?>" />
	</div>

	<label>Interval</label>
	<div>
		<input type="text" name="interval" value="<?=$this->row['interval']?>" />
		<select name="unit">
			<option value="seconds">Seconds</option>
			<option value="hours">Hours</option>
			<option value="days">Days</option>
			<option value="weeks">Weeks</option>
			<option value="months">Months</option>
		</select>
	</div>

	<label>Description</label>
	<div>
		<textarea cols="50" rows="5" name="description"><?=$this->row['description']?></textarea>
	</div>

	<input type="submit" name="save_<?=$edit?>" value="Save" />
</div>
</form>
