# Formatting Output

## JSON

Get ```jq``` (a json processor) with ```brew install jq```.

```jq [options...] filter [files...]```  
The simplest ```jq``` filter is the identity filter ```.``` and it takes its input and produces it unchanged as output. ```jq``` by default pretty-prints all output so the ```.``` filter is basically a json pretty-printer.

## Templates
To display an array using [Go templates](https://blog.gopheracademy.com/advent-2017/using-go-templates/) use  
```
{{range pipeline}} T1 {{end}}
```  
where pipeline is the iterable structure and T1 is the template that is executed on each element.  
The pipeline can be specified as the current context ```{{ . }}```.  
Context in the top level of your template is the data set made available to it. Inside of an iteration, it's the current item in the loop.

## Examples

Pretty-print json.
```Shell
docker info --format '{{json .}}' | jq .
```

Without arrays.
```Shell
docker info --format "{{.Plugins.Volume}}"
docker info --format "{{.OSType}} - {{.Architecture}} CPUs: {{.NCPU}}"
```

With arrays
```Shell
docker inspect --format '{{range .Mounts}} {{.Type}} {{.Name}} {{end}}' mycontainer
gh pr list -R lstein/stable-diffusion --json author,url --template '{{range .}} {{.author.login}} {{.url}} {{end}}'
gh pr list -R lstein/stable-diffusion --json author,url --template '{{range .}} {{tablerow .author.login .url}} {{end}}'

```