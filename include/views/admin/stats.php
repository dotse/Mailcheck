<div class="breadcrumb">
	<a href="/admin">Admin</a> > Statistics
</div>

Filter for specific month
<form method="post">
<select name="year">
	<option value="all" <?=$this->year == null ? 'selected="selected"':''?>>All</option>
	<option value="2010" <?=$this->year == 2010 ? 'selected="selected"':''?>>2010</option>
	<option value="2011" <?=$this->year == 2011 ? 'selected="selected"':''?>>2011</option>
	<option value="2012" <?=$this->year == 2012 ? 'selected="selected"':''?>>2012</option>
	<option value="2013" <?=$this->year == 2013 ? 'selected="selected"':''?>>2013</option>
	<option value="2014" <?=$this->year == 2014 ? 'selected="selected"':''?>>2014</option>
</select>

<select name="month">
	<option value="all" <?=$this->month == null ? 'selected="selected"':''?>>All</option>
<?php for($i=0; $i < count($this->months); $i++): ?>
	<option value="<?=$i+1?>" <?=$this->month == $i+1 ? 'selected="selected"':''?>><?=$this->months[$i]?></option>
<?php endfor; ?>
</select>

<input type="submit" value="Filter" />
</form>
<?php if ($this->interval != ' - '): ?>
<br/>
<div>Selected interval: <?=$this->interval?></div>
<?php endif; ?>

<h3>MailCheck Statistics</h3>
<div class="stats">
	<div>
		<div class="row">
			<div class="title">Total tests executed:</div><div class="value"><?=$this->totalTests?></div>
		</div>
<!--
		<div class="row">
			<div class="title">Avg. tests/day (over last <?=$this->interval == ' - ' ? '30 days' : 'interval'?>):</div><div class="value"><?=$this->avgTestPerDay?></div>
		</div>
-->
		<div class="row">
			<div class="title">Total domains tested:</div><div class="value"><?=$this->totalDomains?></div>
		</div>
		<div class="row">
			<div class="title">Total gold stars:</div><div class="value"><?=$this->totalGold?></div>
		</div>
		<div class="row">
			<div class="title">Gold per test:</div><div class="value"><?=$this->goldPerTest?></div>
		</div>
		<div class="row">
			<div class="title">Tests with gold star:</div><div class="value"><?=$this->totalWithGold?> (<?=$this->totalWithGoldPercent?>%)</div>
		</div>
	</div>

	<div class="clear" style="padding-top: 10px;">
		<h4>Test status</h4>
		<div class="row">
			<div class="title">Plugins per test:</div><div class="value"><?=$this->totalPerTest?></div>
		</div>
		<div class="row">
			<div class="title">Total plugin OK (per test):</div><div class="value"><?=$this->totalOk?> (<?=$this->totalOkPerTest?>)</div>
		</div>
		<div class="row">
			<div class="title">Total plugin warning (per test):</div><div class="value"><?=$this->totalWarning?> (<?=$this->totalWarningPerTest?>)</div>
		</div>
		<div class="row">
			<div class="title">Total plugin error (per test):</div><div class="value"><?=$this->totalError?> (<?=$this->totalErrorPerTest?>)</div>
		</div>
	</div>

	<div class="clear" style="padding-top: 10px">
		<div style="float: left; width: 300px">
			<h4>Top tested domains</h4>
			<table>
				<tr>
					<td>Tests</td>
					<td>Domain</td>
				</tr>
				<?php if (is_array($this->topTested)): ?>
				<?php $c=1; foreach ($this->topTested as $row): ?>
					<tr>
						<td><?=$row['count']?></td>
						<td><?=$row['domain']?></td>
					</tr>
				<?php $c++; endforeach; ?>
				<?php else: ?>
					<tr><td colspan="2">Nothing found</td></tr>	
				<?php endif; ?>
			</table>
		</div>

		<div style="float: left;">
			<h4>Top testers</h4>
			<table>
				<tr>
					<td>Tests</td>
					<td>Email</td>
				</tr>
				<?php if (is_array($this->topTesters)): ?>
				<?php $c=1; foreach ($this->topTesters as $row): ?>
					<tr>
						<td><?=$row['count']?></td>
						<td><?=$row['email']?></td>
					</tr>
				<?php $c++; endforeach; ?>
				<?php else: ?>
					<tr><td colspan="2">Nothing found</td></tr>	
				<?php endif; ?>
			</table>
		</div>
	</div>

	<div class="clear" style="padding-top: 10px">
		<div style="float: left; width: 300px">
			<h4>Top plugins with warnings</h4>
			<table>
				<tr>
					<td>Count</td>
					<td>Plugin</td>
				</tr>
				<?php if (is_array($this->topPluginWarning)): ?>
				<?php $c=1; foreach ($this->topPluginWarning as $row): ?>
					<tr>
						<td><?=$row['count']?></td>
						<td><?=$row['plugin']?></td>
					</tr>
				<?php $c++; endforeach; ?>
				<?php else: ?>
					<tr><td colspan="2">Nothing found</td></tr>	
				<?php endif; ?>
			</table>
		</div>
		<div style="float: left; width: 300px">
			<h4>Top plugins with errors</h4>
			<table>
				<tr>
					<td>Count</td>
					<td>Plugin</td>
				</tr>
				<?php if (is_array($this->topPluginError)): ?>
				<?php $c=1; foreach ($this->topPluginError as $row): ?>
					<tr>
						<td><?=$row['count']?></td>
						<td><?=$row['plugin']?></td>
					</tr>
				<?php $c++; endforeach; ?>
				<?php else: ?>
					<tr><td colspan="2">Nothing found</td></tr>	
				<?php endif; ?>
			</table>
		</div>

	</div>

</div>
