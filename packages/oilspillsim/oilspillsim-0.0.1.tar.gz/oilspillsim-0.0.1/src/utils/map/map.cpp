#include "map.h"
#include <fstream>
#define assertm(exp, msg) if(!exp){std::cout << "\033[1;31m" <<msg<< "\033[0m" << std::endl; assert(0);}
using namespace std;
MAP::MAP(std::string _filepath): mappath(_filepath) // constructor definition
{
    size_t pos = 0;
    std::string aux=mappath;
    std::string token;
    while ((pos = aux.find("/")) != std::string::npos) {
        aux.erase(0, pos + 1);
    }
    mapname.assign(aux);
    string assert_out="map \""+ mapname + "\" does not exist";
    assertm(this->exists(), assert_out);

    this->read_csv();
    ncols=map.size();
    nrows=map.at(0).second.size();

    //obtain_visitable
    for(int col=0; col<ncols;col++)
        for(int row=0; row< nrows;row++)
            if (map.at(col).second[row] ==1)
                visitable.push_back({row,col});

}

MAP::MAP(Eigen::MatrixXi _map) // constructor definition
{
    ncols=_map.cols();
    nrows=_map.rows();
    for (int col=0; col<ncols;col++){
        map.push_back({col, std::vector<int> {}});
        for (int row=0; row< nrows;row++){
            map.at(col).second.push_back(_map(row,col));
            if (_map(row,col) ==1)
                visitable.push_back({row,col});
        }
    }
    mappath.assign("Not provided");
    mapname.assign("Not provided");
}

void MAP::print() const // print function definition
{
    std::cout << "map \"" << mappath << "\"" << std::endl;
    std::vector<std::string> rows(map.at(0).second.size());
    int row=0;
    for(const auto& p : map)
    {
        for(const auto& val : p.second){
            if(val){
                rows[row] += '1';
            }else{
                rows[row] += '0';
            }
            row++;
            }
        row=0;
    }

    for(auto i: rows){
        cout << i << endl;
    }
};

bool MAP::exists() // print function definition
{
    std::ifstream file(mappath);
    return file.good();
};


void MAP::read_csv(){
    // Reads a CSV file into a vector of <int, vector<int>> pairs where
    // each pair represents <column, column values>

    
    // Helper vars
    std::string line,colname;
    int col_number;
    int val=0;
    ////////////////////////////////////////////
    // get the delimiter from read
    /////////////////////////////////////////

    bool founddel=false;
    std::ifstream myFile2(mappath);
    if(!myFile2.is_open()) throw std::runtime_error("Could not open file");
    if(myFile2.good())
    {
        // Extract the first line in the file
        std::getline(myFile2, line);

        // Create a stringstream from line
        std::stringstream ss(line);

        // Extract each integer
        while( !founddel && (ss >> val)){
            // If the next token is not a comma, ignore it and move on
            if(ss.peek() == ',') {
                delimiter=',';
                founddel=true;
            }else if(ss.peek() == ' ') {
                delimiter=' ';
                founddel=true;
            }else if(ss.peek() == ';') {
                delimiter=';';
                founddel=true;
            }else{
                ss.ignore();
            }
        }
    }
    myFile2.close();
    if(!founddel) throw std::runtime_error("Could not recognise delimiter in map");


    /////////////////////////////////////////
    // read map
    /////////////////////////////////////////

    // Create an input filestream
    std::ifstream myFile(mappath);

    // Make sure the file is open
    if(!myFile.is_open()) throw std::runtime_error("Could not open file");


    // Read the column names
    if(myFile.good())
    {
        // Extract the first line in the file
        std::getline(myFile, line);

        // Create a stringstream from line
        std::stringstream ss(line);

        // Extract each column name
        while(std::getline(ss, colname, delimiter)){
            // Initialize and add <colname, int vector> pairs to map
            map.push_back({col_number++, std::vector<int> {}});
        }
    }
    //read the data of the first raw
    // Create a stringstream of the first line
    std::stringstream ss(line);
    // Keep track of the current column index
    int colIdx = 0;
    // Extract each integer
    while(ss >> val){
        // Add the current integer to the 'colIdx' column's values vector
        map.at(colIdx).second.push_back(val);
        
        // If the next token is a comma, ignore it and move on
        if(ss.peek() == delimiter) ss.ignore();
        
        // Increment the column index
        colIdx++;
    }

    // Read data, line by line
    while(std::getline(myFile, line))
    {
        // Create a stringstream of the current line
        std::stringstream ss(line);
        
        // Keep track of the current column index
        int colIdx = 0;
        
        // Extract each integer
        while(ss >> val){
            
            // Add the current integer to the 'colIdx' column's values vector
            map.at(colIdx).second.push_back(val);
            
            // If the next token is a comma, ignore it and move on
            if(ss.peek() == delimiter) ss.ignore();
            
            // Increment the column index
            colIdx++;
        }
    }



    // Close file
    myFile.close();

}


