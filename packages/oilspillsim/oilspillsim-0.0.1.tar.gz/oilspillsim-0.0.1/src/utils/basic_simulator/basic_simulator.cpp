#include "basic_simulator.h"
using namespace std;

// #define LOG_EVERYTHING_SIM

SIMULATOR::SIMULATOR(std::string _filepath, double _dt, double _kw, double _kc, double _gamma, double _flow, int _number_of_sources, int _max_contamination_value, int _source_fuel, int _random_seed, bool _triangular): dt(_dt),kw(_kw),kc(_kc),gamma(_gamma),flow(_flow),number_of_sources(_number_of_sources), max_contamination_value(_max_contamination_value), source_fuel(_source_fuel), random_seed(_random_seed), triangular(_triangular)
{
    mapa = new MAP(_filepath);
    source_points = Eigen::MatrixXi(2,number_of_sources);
    y = Eigen::VectorXi::LinSpaced(mapa->ncols, 0, mapa->ncols).rowwise().replicate(mapa->nrows);
    x = Eigen::RowVectorXi::LinSpaced(mapa->nrows, 0, mapa->nrows).colwise().replicate(mapa->ncols);
    // mapa->print();

    if(random_seed == -1){
        gen =  std::mt19937(rd());
        cout << "no seed specified (-1), using random seed" << endl;
    }else{
        gen =  std::mt19937(random_seed);
    }

    #ifdef LOG_EVERYTHING_SIM
        cout << "found map of " << mapa->ncols << " colums and " << mapa->nrows << " rows" << endl;
        mapa->print();
    #endif


    // generating 5x5 kernel 
    double r, s = 2.0 * sigma * sigma; 
    for (int x = -2; x <= 2; x++) { 
        for (int y = -2; y <= 2; y++) { 
            r = sqrt(x * x + y * y); 
            GKernel[x + 2][y + 2] = (exp(-(r * r) / s)) / (M_PI * s); 
            max_kernel += GKernel[x + 2][y + 2]; 
        } 
    } 
}

SIMULATOR::SIMULATOR(Eigen::MatrixXi _base_matrix, double _dt, double _kw, double _kc, double _gamma, double _flow, int _number_of_sources, int _max_contamination_value, int _source_fuel, int _random_seed, bool _triangular): dt(_dt),kw(_kw),kc(_kc),gamma(_gamma),flow(_flow),number_of_sources(_number_of_sources), max_contamination_value(_max_contamination_value), source_fuel(_source_fuel), random_seed(_random_seed), triangular(_triangular)
{
    mapa = new MAP(_base_matrix);
    source_points = Eigen::MatrixXi(2,number_of_sources);
    y = Eigen::VectorXi::LinSpaced(mapa->ncols, 0, mapa->ncols).rowwise().replicate(mapa->nrows);
    x = Eigen::RowVectorXi::LinSpaced(mapa->nrows, 0, mapa->nrows).colwise().replicate(mapa->ncols);
    // mapa->print();

    if(random_seed == -1){
        gen =  std::mt19937(rd());
        cout << "no seed specified (-1), using random seed" << endl;
    }else{
        gen =  std::mt19937(random_seed);
    }

    #ifdef LOG_EVERYTHING_SIM
        cout << "found map of " << mapa->ncols << " colums and " << mapa->nrows << " rows" << endl;
        mapa->print();
    #endif


    // generating 5x5 kernel 
    double r, s = 2.0 * sigma * sigma; 
    for (int x = -2; x <= 2; x++) { 
        for (int y = -2; y <= 2; y++) { 
            r = sqrt(x * x + y * y); 
            GKernel[x + 2][y + 2] = (exp(-(r * r) / s)) / (M_PI * s); 
            max_kernel += GKernel[x + 2][y + 2]; 
        } 
    } 
}


void SIMULATOR::reset(int _seed){ 
    if(_seed != -1){
        random_seed = _seed;
        gen =  std::mt19937(random_seed);
    #ifdef LOG_EVERYTHING_SIM
        cout << "Reset with seed " <<random_seed  << endl;
    }else{
        cout << "Reset with same seed " <<random_seed  << endl;
    #endif
    }
    /* RESET THE ENV VARIABLES*/
    if(!init){
        init=true;
    }

    done=false;
    step_counter =0;

    //Generate the source points
    std::uniform_int_distribution<> distr(0, mapa->visitable.size()-1); // define the range
    
    for(int i=0;i<number_of_sources;i++){
        int index=distr(gen);
        source_points(0,i)=mapa->visitable[index].first;
        source_points(1,i)=mapa->visitable[index].second;
    }
    // else{
    //     source_points = _source_points.transpose();
    //     for(int i=0; i< source_points.cols();i++){
    //         std::pair<int, int> item(source_points(0,i), source_points(1,i));
    //         if (std::find(mapa->visitable.begin(), mapa->visitable.end(), item) == mapa->visitable.end() ){ 
    //             cout << "forced source point " << item.first << " " << item.second << " is not in a visitable point in the map" << endl;
    //             assert(false);
    //         }
    //     }
    // }
    #ifdef LOG_EVERYTHING_SIM
        cout << "source_points shape" <<source_points.rows()  << "x" << source_points.cols()<< endl;
        cout << "source_points: " <<source_points<< endl;
    #endif

    std::uniform_real_distribution<> dist_wind(-1, 1); // define the range
    
    //generate wind speed
    wind_speed = Eigen::VectorXd(2);
    wind_speed << dist_wind(gen),dist_wind(gen);
    // }else{
    //     //hardcoded wind??
    //     wind_speed=wind;
    // }
    #ifdef LOG_EVERYTHING_SIM
        cout << "wind speed is [" << dt * kw *(wind_speed.transpose()) << "]" <<endl;
    #endif

    //initialize
    contamination_position=source_points.cast<double>();

    if(!triangular){
        //Random current vector field
        std::uniform_int_distribution<> distr_mapx(0,mapa->ncols-1); // define the range
        std::uniform_int_distribution<> distr_mapy(0,mapa->nrows-1); // define the range
        std::uniform_real_distribution<> distr2(3, 100); // define the range

        Eigen::MatrixXi x0 = Eigen::MatrixXi::Constant(mapa->ncols, mapa->nrows, distr_mapx(gen));
        Eigen::MatrixXi y0 = Eigen::MatrixXi::Constant(mapa->ncols, mapa->nrows, distr_mapy(gen));
        Eigen::MatrixXd aux1=(x-x0).cast<double>();
        Eigen::MatrixXd aux2=(y-y0).cast<double>();
        u=(aux1*(EIGEN_PI/distr2(gen))).array().sin()*((aux2*(M_PI/distr2(gen))).array().cos());
        v=-(aux1*(EIGEN_PI/distr2(gen))).array().cos()*((aux2*(M_PI/distr2(gen))).array().sin());
        // }else{
        //     // if(_u.cols()!=mapa->ncols || _u.rows()!=mapa->nrows || _v.cols()!=mapa->ncols || _v.rows()!=mapa->nrows)
        //     // {
        //     //     cout << "bad u or v shape " << _u.cols() << "x" << _u.rows() << "  " <<  _v.cols() << "x" << _v.rows() << " when it should be "<< mapa->ncols  << " " << mapa->nrows<< endl;
        //     //     assert(false);
        //     // }
        //     u=_u;
        //     v=_v;
        // }
    }else{ //currents generated from start point
        u = Eigen::MatrixXd::Constant(mapa->ncols, mapa->nrows,0);
        v = Eigen::MatrixXd::Constant(mapa->ncols, mapa->nrows,0);
        double xt= source_points(0,0);
        double yt= source_points(1,0);
        for(int m=1;m<mapa->ncols-1;m++){
            for(int n=1;n<mapa->nrows-1;n++){
                if(n-xt == 0 && m-yt ==0){
                    std::uniform_int_distribution<> distr_start(-1, 1); // define the range
                    u(m,n)=distr_start(gen)*triangular_magnitude;
                    v(m,n)=distr_start(gen)*triangular_magnitude;
                }else{
                    if(abs(xt-n)>abs(m-yt)){
                        v(m,n)=triangular_magnitude*(n-xt)/pow(abs(n-xt),triangular_dilution);
                    }else{
                        u(m,n)=triangular_magnitude*(m-yt)/pow(abs(m-yt),triangular_dilution);
                    }
                }

            }
        }
    }

    //density map
    density = Eigen::MatrixXi::Constant(mapa->nrows,mapa->ncols,0); //initialize to -1
    //put to 0 map points
    // for (auto point: mapa->visitable){
    //     density(point.first,point.second)=0;
    // }
    // initialize first particles in density
    for(int i=0; i<contamination_position.cols();i++){
        density((int)contamination_position(0,i),(int)contamination_position(1,i))++;
    }


    #ifdef LOG_EVERYTHING_SIM
        cout << "map shape" << mapa->ncols  << " " << mapa->nrows<< endl;
        cout << "contamination_position shape" <<contamination_position.rows()  << " " << contamination_position.cols()<< endl;
        cout << "u shape" <<u.rows()  << " " << u.cols()<< endl;
        cout << "v shape" <<v.rows()  << " " << v.cols()<< endl;
        // cout << "Visitable:" << endl;
        // for(auto i: mapa->visitable){
        //     cout << "[" << i.first << "," << i.second << "], ";
        // } 
        cout << endl;
    #endif
}


void SIMULATOR::step(){
    assert(init); //"Environment not initiated!"
    //update particles positions
    std::uniform_real_distribution<> distrandom(-2, 2); // define the range
    for(int i=0;i<contamination_position.cols();i++){
        //compute components of the particle movement
        Eigen::VectorXd v_random = Eigen::VectorXd(2);
        v_random << distrandom(gen)*gamma,distrandom(gen)*gamma;
        // else{
        //     v_random = _random.row(i)*gamma;
        // }
        Eigen::VectorXd v_wind = kw*wind_speed;
        Eigen::VectorXd aux(2);
        aux << v((int)contamination_position(1,i),(int)contamination_position(0,i)), u((int)contamination_position(1,i),(int)contamination_position(0,i));
        Eigen::VectorXd v_current = kc *aux; 

        //add new position to the list
        Eigen::VectorXd vnew= contamination_position.col(i) + (dt * (v_wind+ v_current) + v_random);
        #ifdef LOG_EVERYTHING_SIM
        cout << "wind [" << v_wind.transpose() << "]    update position[" << (dt * (v_wind+ v_current) + v_random).cast<int>().transpose() << "]    current [" << v_current.transpose() << "]     random["  <<  v_random.transpose() <<"]" <<endl;
        #endif
        //if particle is not visitable
        if((int)vnew(0)>mapa->nrows-1 || (int)vnew(0) <0|| (int)vnew(1) < 0 || (int)vnew(1)>mapa->ncols-1){ //if out of bounds, remove particle
            #ifdef LOG_EVERYTHING_SIM
            cout << "we got to remove " << contamination_position.col(i).transpose() << endl;
            #endif
            density((int)contamination_position(0,i),(int)contamination_position(1,i))--;
            if(density((int)contamination_position(0,i),(int)contamination_position(1,i)) <0){
                cout << "something weird happened, erased particle where should be none, move out at " << step_counter  << contamination_position.col(i).transpose() << endl;
            }
            this->removeColumn(contamination_position,i);
        }
        else if ( mapa->map.at((int)vnew(1)).second[(int)vnew(0)] ==1){ //if position is not visitable, position wont be updated
            density((int)contamination_position(0,i),(int)contamination_position(1,i))--; //update density and position
            if(density((int)contamination_position(0,i),(int)contamination_position(1,i)) <0){
                cout << "something weird happened, erased particle where should be none, move in at " << step_counter  <<"  " << contamination_position.col(i).transpose() << endl;
                density((int)contamination_position(0,i),(int)contamination_position(1,i))=0;
            }
            
            if(density((int)(vnew(0)),(int)vnew(1))>=max_contamination_value){ //check density before creating new particle
                vnew= get_closest_neighbourgh(vnew);//look for inmediate position next to it if it is full
            }
            contamination_position.col(i)=vnew;
            density((int)contamination_position(0,i),(int)contamination_position(1,i))++;
        }
    }
    //generate new particles
    for(int i=0;i<source_points.cols();i++){
        if(source_fuel>0){
            flow_remainder+=flow;
            while(flow_remainder*dt>1 && source_fuel>0){ //generate as many particles as flow says
                Eigen::VectorXd v_random = Eigen::VectorXd(2);
                v_random << distrandom(gen)*gamma,distrandom(gen)*gamma;
                // else{
                //     v_random = _random.row(i+contamination_position.cols())*gamma;
                // }
                //compute components of the particle movement
                Eigen::VectorXd v_wind = kw*wind_speed;
                Eigen::VectorXd aux(2);
                aux << v(source_points(1,i),source_points(0,i)), u(source_points(1,i),source_points(0,i));
                Eigen::VectorXd v_current = kc *aux; 
                //add new position to the list
                Eigen::VectorXd vnew(2);
                if (apply_forces_at_origin){
                    vnew= source_points.col(i).cast<double>() + (dt * (v_wind+ v_current) + v_random);
                }else{
                    vnew= source_points.col(i).cast<double>() +  v_random;
                }
                // std::pair<int, int> item(vnew(0), vnew(1));
                //if particle is not visitable, dont update pos
                if((int)vnew(0)>mapa->nrows-1 || (int)vnew(0) <0|| (int)vnew(1) < 0 || (int)vnew(1)>mapa->ncols-1){
                    cout << "something really bad happened with simulator, particle spawned outside map" << endl;
                    flow_remainder--; //to avoid infinite wait. if there is no fuel to generate, dont
                    continue;
                }
                if ( mapa->map.at((int)vnew(1)).second[(int)vnew(0)] ==0){ 
                    vnew= source_points.col(i).cast<double>();
                }
                contamination_position.conservativeResize(contamination_position.rows(), contamination_position.cols()+1);
                if(density((int)(vnew(0)),(int)vnew(1))>=max_contamination_value){ //check density before creating new particle
                    vnew= get_closest_neighbourgh(vnew);//look for inmediate position next to it if it is full
                }
                contamination_position.col(contamination_position.cols()-1)=vnew;
                density((int)contamination_position(0,contamination_position.cols()-1),(int)contamination_position(1,contamination_position.cols()-1))++;
                source_fuel--;
                flow_remainder--;
            }
        }
    }
    step_counter++;
}


void SIMULATOR::removeColumn(Eigen::MatrixXd &matrix, unsigned int colToRemove)
{
    unsigned int numRows = matrix.rows();
    unsigned int numCols = matrix.cols()-1;

    if( colToRemove < numCols )
        matrix.block(0,colToRemove,numRows,numCols-colToRemove) = matrix.rightCols(numCols-colToRemove);

    matrix.conservativeResize(numRows,numCols);
}


Eigen::MatrixXd SIMULATOR::get_normalized_density(bool gaussian){
    Eigen::MatrixXd density_d = Eigen::MatrixXd::Zero(mapa->nrows,mapa->ncols);
    if(gaussian==false){
        for (auto point: mapa->visitable){
            density_d(point.first,point.second)=((double)density(point.first,point.second))/((double)(max_contamination_value));
        }
    }else{
        for (auto point: mapa->visitable){
            double kernel=max_kernel;
            for (int x = -2; x <= 2; x++) { 
                for (int y = -2; y <= 2; y++) { 
                    if(point.first+x >1 && point.first+x < mapa->nrows-2 && point.second+y >1 && point.second+y <mapa->ncols -1){
                        if (mapa->map.at(point.second+y).second[point.first+x] ==0)
                            kernel-=GKernel[x+2][y+2];
                        else
                            density_d(point.first,point.second)+=((double)density(point.first+x,point.second+y))*GKernel[x+2][y+2]/((double)(max_contamination_value));
                    }else{
                        kernel-=GKernel[x+2][y+2];
                    }
                }
            }
            density_d(point.first,point.second)/=kernel;
        }
    }
    return density_d;
}


Eigen::VectorXd SIMULATOR::get_closest_neighbourgh(Eigen::VectorXd position){
    Eigen::VectorXd test(2);
    int radius=1;
    while(true){ //get contouring points
        if(radius>mapa->ncols/3+mapa->nrows/3){
            cout << "looked for too long" <<endl;
            return position;
        }
        Eigen::MatrixXd available = Eigen::MatrixXd::Constant(2, 1, -1);;
        for(int i=-radius;i<=radius;i++){
            for(int j=-radius;j<=radius;j++){
                if(int(sqrt(i*i+j*j))==radius){
                    if((int)(position(0)+i)>mapa->nrows-1 || (int)(position(0)+i) <0|| (int)(position(1)+j) < 0 || (int)(position(1)+j)>mapa->ncols-1)
                        continue; //if not visitable, look for next
                    if(mapa->map.at((int)(position(1)+j)).second[(int)(position(0)+i)] !=1) //if it is not visitable
                        continue;
                    if(density((int)(position(0)+i),(int)(position(1)+j))<max_contamination_value){//is  a valid position
                        available(0,available.cols()-1)=position(0)+i;
                        available(1,available.cols()-1)=position(1)+j;
                        available.conservativeResize(2, available.cols()+1);
                    }
                }
            }
        }
        radius++;
        if(available.cols()==1 && available(0,0) == -1){ //if we didnt find any available point
            continue;
        }
        //we found a point, pick a random position
        std::uniform_int_distribution<> distr_available(0,available.cols()-2);
        return available.col(distr_available(gen));
    }
    return position;
}

//TODO: check integrity of data