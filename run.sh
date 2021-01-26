#conda init bash
#conda activate ile-de-france
# -> do before run

paramfile=$1

# backup config
mv config.yml config_bk.yml

while read line; do
  echo "Run:$line"
  name="$(echo $line | cut -d';' -f1)"
  price="$(echo $line | cut -d';' -f2)"
  iters="$(echo $line | cut -d';' -f3)"
  seed="$(echo $line | cut -d';' -f4)"
  
  echo "Toll name = $name"
  echo "Toll price = $price"
  echo "Iterations = $iters"
  echo "Seed = $seed"
  
  # update config file
  while IFS= read -r confline; do
    #echo "[$confline]"
    if [[ $confline =~ "cordon_toll_price" ]]; then
       echo "  cordon_toll_price: $price" >> config.yml
    else
       if [[ $confline =~ "cordon_toll_name" ]]; then
           echo "  cordon_toll_name: $name" >> config.yml
       else
           echo "$confline" >> config.yml
       fi
    fi
  done <config_bk.yml

  # run toll file update
  python3 -m synpp

  # cat config.yml
  rm config.yml

  cd output
  java -Xmx16G -cp ile_de_france_run.jar org.eqasim.ile_de_france.RunSimulation --config-path ile_de_france_config.xml --config:global.randomSeed $seed --config:controler.lastIteration $iters --config:controler.writeTripsInterval 1 --config:counts.writeCountsInterval 1 --config:planCalcScore.scoringParameters[marginalUtilityOfMoney="0.0"].marginalUtilityOfMoney 1.0

  #cat config.yml

  mv simulation_output "simulation_output_"$name"_"$price"_"$iters"_"$seed
  cd ..
done <$paramfile

mv config_bk.yml config.yml


#python3 -m synpp
#cd output
#java -Xmx14G -cp ile_de_france_run.jar org.eqasim.ile_de_france.RunSimulation --config-path ile_de_france_config.xml
#mv simulation_output simulation_output_1
#cd ..
#mv config.yml config_tmp.yml
#mv config2.yml config.yml
#python3 -m synpp
#cd output
#java -Xmx14G -cp ile_de_france_run.jar org.eqasim.ile_de_france.RunSimulation --config-path ile_de_france_config.xml
#mv simulation_output simulation_output_2
#cd ..
#mv config.yml config2.yml
#mv config_tmp.yml config.yml

