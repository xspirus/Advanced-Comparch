#ifndef BRANCH_PREDICTOR_H
#define BRANCH_PREDICTOR_H

#include <sstream> // std::ostringstream
#include <cmath>   // pow()
#include <cstring> // memset()
#include <vector>

/**
 * A generic BranchPredictor base class.
 * All predictors can be subclasses with overloaded predict() and update()
 * methods.
 **/

class BranchPredictor
{
public:
    BranchPredictor() : correct_predictions(0), incorrect_predictions(0) {};
    ~BranchPredictor() {};

    virtual bool predict(ADDRINT ip, ADDRINT target) = 0;
    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) = 0;
    virtual string getName() = 0;

    UINT64 getNumCorrectPredictions() { return correct_predictions; }
    UINT64 getNumIncorrectPredictions() { return incorrect_predictions; }

    void resetCounters() { correct_predictions = incorrect_predictions = 0; };

protected:
    void updateCounters(bool predicted, bool actual) {
        if (predicted == actual)
            correct_predictions++;
        else
            incorrect_predictions++;
    };

private:
    UINT64 correct_predictions;
    UINT64 incorrect_predictions;
};

class NbitPredictor : public BranchPredictor
{
public:
    NbitPredictor(unsigned index_bits_, unsigned cntr_bits_)
        : BranchPredictor(), index_bits(index_bits_), cntr_bits(cntr_bits_) {
        table_entries = 1 << index_bits;
        TABLE = new unsigned long long[table_entries];
        memset(TABLE, 0, table_entries * sizeof(*TABLE));

        COUNTER_MAX = (1 << cntr_bits) - 1;
    };
    ~NbitPredictor() { delete TABLE; };

    virtual bool predict(ADDRINT ip, ADDRINT target) {
        unsigned int ip_table_index = ip % table_entries;
        unsigned long long ip_table_value = TABLE[ip_table_index];
        unsigned long long prediction = ip_table_value >> (cntr_bits - 1);
        return (prediction != 0);
    };

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
        unsigned int ip_table_index = ip % table_entries;
        if (actual) {
            if (TABLE[ip_table_index] < COUNTER_MAX)
                TABLE[ip_table_index]++;
        } else {
            if (TABLE[ip_table_index] > 0)
                TABLE[ip_table_index]--;
        }

        updateCounters(predicted, actual);
    };

    virtual string getName() {
        std::ostringstream stream;
        stream << "Nbit-" << pow(2.0,double(index_bits)) / 1024.0 << "K-" << cntr_bits;
        return stream.str();
    }

private:
    unsigned int index_bits, cntr_bits;
    unsigned int COUNTER_MAX;

    /* Make this unsigned long long so as to support big numbers of cntr_bits. */
    unsigned long long *TABLE;
    unsigned int table_entries;
};

class BTBEntry {
private:
    ADDRINT addr;
    ADDRINT target;
public:
    BTBEntry(ADDRINT addr, ADDRINT target) {
        this->addr = addr;
        this->target = target;
    }
    ADDRINT getAddr() {
        return this->addr;
    }
    ADDRINT getTarget() {
        return this->target;
    }
};

// Fill in the BTB implementation ...
class BTBPredictor : public BranchPredictor
{
public:
	BTBPredictor(int btb_lines, int btb_assoc)
	     : BranchPredictor(), table_lines(btb_lines), table_assoc(btb_assoc), correct_target(0)
	{
		entries = new std::vector<BTBEntry>[table_lines];
	}

	~BTBPredictor() {
        delete [] entries;
	}

    virtual bool predict(ADDRINT ip, ADDRINT target) {
		/* ... fill me ... */
        BTBEntry entry(ip, target);
        return (this->find(entry) != 0);
	}

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
		/* ... fill me ... */
        if (actual && predicted) {              /* correct prediction */
            BTBEntry entry(ip, target);
            ADDRINT predTarget = this->find(entry);
            if (predTarget == target) {
                this->correct_target++;
            }
        } else if (predicted && !(actual)) {    /* delete from BTB */
            this->erase(ip);
        } else if (actual && !(predicted)) {    /* put in BTB */
            BTBEntry entry(ip, target);
            this->replace(entry);
        }
        updateCounters(predicted, actual);
	}

    virtual string getName() {
        std::ostringstream stream;
		stream << "BTB-" << table_lines << "-" << table_assoc;
		return stream.str();
	}

    UINT64 getNumCorrectTargetPredictions() {
		return this->correct_target;
	}

private:

	unsigned int table_lines, table_assoc;
    UINT64 correct_target;
    std::vector<BTBEntry> *entries;

    ADDRINT find(BTBEntry & e) {
        int index = e.getAddr() % this->table_lines;
        std::vector<BTBEntry>::iterator it;
        for (it = entries[index].begin(); it != entries[index].end(); ++it) {
            if (it->getAddr() == e.getAddr()) {
                entries[index].erase(it);
                entries[index].push_back(e);
                return it->getTarget();
            }
        }
        return 0;
    }

    void replace(BTBEntry & e) {
        int index = e.getAddr() % this->table_lines;
        std::vector<BTBEntry>::iterator it;
        entries[index].push_back(e);
        if (entries[index].size() > this->table_assoc) {
            entries[index].erase(entries[index].begin());
            return;
        }
        return;
    }

    void erase(ADDRINT addr) {
        int index = addr % this->table_lines;
        std::vector<BTBEntry>::iterator it;
        for (it = entries[index].begin(); it != entries[index].end(); ++it) {
            if (it->getAddr() == addr) {
                entries[index].erase(it);
                return;
            }
        }
        return;
    }

};

class StaticTaken : public BranchPredictor {

public:
    StaticTaken() : BranchPredictor() {}
    ~StaticTaken() {}

    virtual bool predict(ADDRINT ip, ADDRINT target) {
        return true;
    }

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
        updateCounters(predicted, actual);
    }

    virtual string getName() {
        std::ostringstream stream;
        stream << "StaticTaken";
        return stream.str();
    }

};

class BTFNT : public BranchPredictor {

public:
    BTFNT() : BranchPredictor() {}
    ~BTFNT() {}

    virtual bool predict(ADDRINT ip, ADDRINT target) {
        return (target < ip);
    }

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
        updateCounters(predicted, actual);
    }

    virtual string getName() {
        std::ostringstream stream;
        stream << "BTFNT";
        return stream.str();
    }

};

class LocalHistoryTwoLevel : public BranchPredictor {

private:
    unsigned int PHTindex, PHTcntr;
    unsigned int BHTindex, BHTcntr;
    unsigned int PHTentries, BHTentries;
    unsigned long long int *PHT;
    unsigned long long int *BHT;

    unsigned int PHTmod, BHTmod;

    unsigned int COUNTER_MAX;

public:

    LocalHistoryTwoLevel(unsigned int PHTindex,
                        unsigned int PHTcntr,
                        unsigned int BHTindex,
                        unsigned int BHTcntr) : BranchPredictor() {
        this->PHTindex = PHTindex;
        this->PHTcntr = PHTcntr;
        this->BHTindex = BHTindex;
        this->BHTcntr = BHTcntr;

        this->PHTentries = 1 << this->PHTindex;
        this->BHTentries = 1 << this->BHTindex;

        this->PHT = new unsigned long long int [PHTentries];
        this->BHT = new unsigned long long int [BHTentries];

        memset(PHT, 0, PHTentries * sizeof(*PHT));
        memset(BHT, 0, BHTentries * sizeof(*BHT));

        /* Need (PHTindex - BHTcntr) bits shifted BHTcntr bits left */
        this->PHTmod = 1 << (this->PHTindex - this->BHTcntr);
        this->BHTmod = this->BHTentries;

        /* For 2bit PHT predictor */
        COUNTER_MAX = (1 << this->PHTcntr) - 1;
    }

    ~LocalHistoryTwoLevel() {
        delete [] PHT;
        delete [] BHT;
    }

    virtual bool predict(ADDRINT ip, ADDRINT target) {
        unsigned int PHTinx, BHTinx;

        PHTinx = (ip % this->PHTmod) << this->BHTcntr;
        BHTinx = ip % this->BHTmod;

        /**
         * 1 << BHTcntr = max number ( + 1) for a BHTentry.
         * So with mod we restrict the non zero bits we get
         * from the BHT, which are at most BHTcntr.
         */
        PHTinx = PHTinx | (BHT[BHTinx] % (1 << this->BHTcntr));

        return ((PHT[PHTinx] >> (this->PHTcntr - 1)) != 0);
    }

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
        unsigned int PHTinx, BHTinx;

        PHTinx = (ip % this->PHTmod) << this->BHTcntr;
        BHTinx = ip % this->BHTmod;

        /**
         * 1 << BHTcntr = max number ( + 1) for a BHTentry.
         * So with mod we restrict the non zero bits we get
         * from the BHT, which are at most BHTcntr.
         */
        PHTinx = PHTinx | (BHT[BHTinx] % (1 << this->BHTcntr));

        /* Shift out oldest outcome */
        BHT[BHTinx] = BHT[BHTinx] << 1;

        /**
         * To shift in new outcome we use this:
         *   if actual is one then just increment BHTentry by 1
         *     which is equivalent to place bit #0 to 1,
         *     because previously we had shifted left so bit #0 is 0.
         *   else do nothing for BHTentry
         */
        if (actual) {
            /* Shift in newest outcome */
            BHT[BHTinx]++;
            if (PHT[PHTinx] < COUNTER_MAX)
                PHT[PHTinx]++;
        } else {
            if (PHT[PHTinx] > 0)
                PHT[PHTinx]--;
        }

        updateCounters(predicted, actual);
    }

    virtual string getName() {
        std::ostringstream stream;
        stream << "LocalHistoryTwoLevel-"
               << "PHT-" << pow(2.0, double(PHTindex)) / 1024.0 << "K-" << PHTcntr << "-"
               << "BHT-" << pow(2.0, double(BHTindex)) / 1024.0 << "K-" << BHTcntr;
        return stream.str();
    }

};

class GlobalHistoryTwoLevel : public BranchPredictor {

private:
    unsigned int PHTindex, PHTcntr;
    unsigned int BHRcntr;

    unsigned int PHTentries;
    unsigned long long int *PHT;
    unsigned long long int  BHR;

    unsigned int PHTmod;

    unsigned int COUNTER_MAX;

public:

    GlobalHistoryTwoLevel(unsigned int PHTindex,
                            unsigned int PHTcntr,
                            unsigned int BHRcntr
                        ) : BranchPredictor() {
        this->PHTindex = PHTindex;
        this->PHTcntr = PHTcntr;
        this->BHRcntr = BHRcntr;

        this->PHTentries = 1 << this->PHTindex;

        this->PHT = new unsigned long long int [PHTentries];

        memset(PHT, 0, PHTentries * sizeof(*PHT));
        this->BHR = 0;

        /* Need (PHTindex - BHRcntr) bits shifted BHRcntr bits left */
        this->PHTmod = 1 << (this->PHTindex - this->BHRcntr);

        /* For Nbit PHT predictor */
        COUNTER_MAX = (1 << this->PHTcntr) - 1;
    }

    ~GlobalHistoryTwoLevel() {
        delete [] PHT;
    }

    virtual bool predict(ADDRINT ip, ADDRINT target) {
        unsigned int PHTinx;

        PHTinx = (ip % this->PHTmod) << this->BHRcntr;

        /**
         * 1 << BHRcntr = max number ( + 1) for a BHRentry.
         * So with mod we restrict the non zero bits we get
         * from the BHR, which are at most BHTcntr.
         */
        PHTinx = PHTinx | (BHR % (1 << this->BHRcntr));

        return ((PHT[PHTinx] >> (this->PHTcntr - 1)) != 0);
    }

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
        unsigned int PHTinx;

        PHTinx = (ip % this->PHTmod) << this->BHRcntr;

        /**
         * 1 << BHRcntr = max number ( + 1) for BHR value.
         * So with mod we restrict the non zero bits we get
         * from the BHR, which are at most BHRcntr.
         */
        PHTinx = PHTinx | (BHR % (1 << this->BHRcntr));

        /* Shift out oldest outcome */
        BHR = BHR << 1;

        /**
         * To shift in new outcome we use this:
         *      if actual is one then just increment BHR by 1
         *          which is equivalent to place bit #0 to 1,
         *          because previously we had shifted left so bit #0 is 0.
         *      else do nothing for BHR
         */
        if (actual) {
            /* Shift in newest outcome */
            BHR++;
            if (PHT[PHTinx] < COUNTER_MAX)
                PHT[PHTinx]++;
        } else {
            if (PHT[PHTinx] > 0)
                PHT[PHTinx]--;
        }

        updateCounters(predicted, actual);
    }

    virtual string getName() {
        std::ostringstream stream;
        stream << "GlobalHistoryTwoLevel-"
               << "PHT-" << pow(2.0, double(PHTindex)) / 1024.0 << "K-" << PHTcntr << "-"
               << "BHR-" << BHRcntr;
        return stream.str();
    }

};

class TournamentLocalNbit : public BranchPredictor {

private:
    unsigned int index, cntr;
    unsigned int entries;

    unsigned long long int *table;
    unsigned int COUNTER_MAX;

    bool nbitPred, localPred;

    NbitPredictor *nbit;
    LocalHistoryTwoLevel *local;

public:

    TournamentLocalNbit(unsigned int index,
                        unsigned int cntr,
                        unsigned int nbitIndex,
                        unsigned int nbitCntr,
                        unsigned int PHTindex,
                        unsigned int PHTcntr,
                        unsigned int BHTindex,
                        unsigned int BHTcntr
                    ) : BranchPredictor() {
        this->index = index;
        this->cntr = cntr;
        this->entries = 1 << this->index;

        table = new unsigned long long int [this->entries];
        memset(table, 0, sizeof(*table) * this->entries);

        COUNTER_MAX = (1 << this->cntr) - 1;

        nbitPred = false;
        localPred = false;

        nbit = new NbitPredictor(nbitIndex, nbitCntr);
        local = new LocalHistoryTwoLevel(PHTindex, PHTcntr, BHTindex, BHTcntr);
    }

    ~TournamentLocalNbit() {
        delete [] table;
    }

    virtual bool predict(ADDRINT ip, ADDRINT target) {
        nbitPred = nbit->predict(ip, target);
        localPred = local->predict(ip, target);
        unsigned int index = ip % this->entries;
        if ((table[index] >> (this->cntr - 1)) > 0) {
            return localPred;
        } else {
            return nbitPred;
        }
        return false;
    }

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
        nbit->update(nbitPred, actual, ip, target);
        local->update(localPred, actual, ip, target);
        /* For meta */
        unsigned int index = ip % this->entries;
        if (nbitPred != localPred) {
            if (nbitPred == actual && table[index] > 0)
                table[index]--;
            else if (localPred == actual && table[index] < COUNTER_MAX)
                table[index]++;
        }
        updateCounters(predicted, actual);
    }

    virtual string getName() {
        std::ostringstream stream;
        stream << "Tournament-" << nbit->getName() << "-" << local->getName();
        return stream.str();
    }

};

class TournamentGlobalNbit : public BranchPredictor {

private:
    unsigned int index, cntr;
    unsigned int entries;

    unsigned long long int *table;
    unsigned int COUNTER_MAX;

    bool nbitPred, globalPred;

    NbitPredictor *nbit;
    GlobalHistoryTwoLevel *global;

public:

    TournamentGlobalNbit(unsigned int index,
                        unsigned int cntr,
                        unsigned int nbitIndex,
                        unsigned int nbitCntr,
                        unsigned int PHTindex,
                        unsigned int PHTcntr,
                        unsigned int BHRcntr
                    ) : BranchPredictor() {
        this->index = index;
        this->cntr = cntr;
        this->entries = 1 << this->index;

        table = new unsigned long long int [this->entries];
        memset(table, 0, sizeof(*table) * this->entries);

        COUNTER_MAX = (1 << this->cntr) - 1;

        nbitPred = false;
        globalPred = false;

        nbit = new NbitPredictor(nbitIndex, nbitCntr);
        global = new GlobalHistoryTwoLevel(PHTindex, PHTcntr, BHRcntr);
    }

    ~TournamentGlobalNbit() {
        delete [] table;
    }

    virtual bool predict(ADDRINT ip, ADDRINT target) {
        nbitPred = nbit->predict(ip, target);
        globalPred = global->predict(ip, target);
        unsigned int index = ip % this->entries;
        if ((table[index] >> (this->cntr - 1)) > 0) {
            return globalPred;
        } else {
            return nbitPred;
        }
        return false;
    }

    virtual void update(bool predicted, bool actual, ADDRINT ip, ADDRINT target) {
        nbit->update(nbitPred, actual, ip, target);
        global->update(globalPred, actual, ip, target);
        /* For meta */
        unsigned int index = ip % this->entries;
        if (nbitPred != globalPred) {
            if (nbitPred == actual && table[index] > 0)
                table[index]--;
            else if (globalPred == actual && table[index] < COUNTER_MAX)
                table[index]++;
        }
        updateCounters(predicted, actual);
    }

    virtual string getName() {
        std::ostringstream stream;
        stream << "Tournament-" << nbit->getName() << "-" << global->getName();
        return stream.str();
    }

};

#endif
