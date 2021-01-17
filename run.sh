#conda init bash
#conda activate ile-de-france
# -> do before run
python3 -m synpp
cd output
java -Xmx14G -cp ile_de_france_run.jar org.eqasim.ile_de_france.RunSimulation --config-path ile_de_france_config.xml
mv simulation_output simulation_output_1
cd ..
mv config.yml config_tmp.yml
mv config2.yml config.yml
python3 -m synpp
cd output
java -Xmx14G -cp ile_de_france_run.jar org.eqasim.ile_de_france.RunSimulation --config-path ile_de_france_config.xml
mv simulation_output simulation_output_2
cd ..
mv config.yml config2.yml
mv config_tmp.yml config.yml

