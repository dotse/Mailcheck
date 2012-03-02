<div class="breadcrumb">
	<a href="/admin">Admin</a> > Bug reports
</div>

<table>
	<th>Reporter email</th>
	<th>Reported</th>
	<th>Description</th>
	<th>&nbsp;</th>
<?php 
$i="#ffffff";
foreach($this->list as $l): 
  if ($i == "#ffffff") {$i="#e0e0e0";} else {$i="#ffffff";}
?>
	<tr style='background: <?=$i?>'>
		<td><a href="mailto: <?=$l['email']?>"><?=$l['email']?></a></td>
		<td><?=substr($l['created'], 0, 19)?></td>
		<td><?=$l['description']?></td>
		<td><a href="/admin/bugreports.php?view&id=<?=$l['id']?>">View</a>
	</tr>
<?php endforeach; ?>
</table>
