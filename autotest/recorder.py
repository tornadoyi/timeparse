import platform
import codecs
import os
if platform.system() != "Windows": from progressive.bar import Bar

class Case(object):
    def __init__(self,
                 tag=None,
                 timestamp=None,
                 question=None,
                 bot_answers=None,
                 expect_answers=None,
                 result=None):
        self.tag = tag
        self.timestamp = timestamp
        self.question = question
        self.bot_answers = bot_answers
        self.expect_answers = expect_answers
        self.result = result

    def __str__(self):
        string = u""
        if self.tag: string += u"{0} ".format(self.tag)
        if self.timestamp: string += u"{0} ".format(self.timestamp)
        if self.question: string += u"{0} ".format(self.question)
        if self.result != None: string += u"result: {0}".format('success' if self.result else 'failed')
        string += "\n"

        if self.bot_answers:
            string += u"bot answers:\n"
            for answer in self.bot_answers: string += u'  {0}\n'.format(answer)

        if self.expect_answers:
            string += u"expect answers:\n"
            for answer in self.expect_answers: string += u'  {0}\n'.format(unicode(str(answer), encoding="utf8"))

        return string

class Recorder(object):

    def __init__(self, args):
        self.cases = []
        self.success_cases = []
        self.failed_cases = []
        self.show_progress = args.show_progress

    @property
    def case_count(self): return len(self.cases)

    @property
    def success_count(self): return len(self.success_cases)

    @property
    def failed_count(self): return len(self.failed_cases)

    @property
    def accuracy(self): return float(self.success_count) / float(self.case_count)

    def add_case(self, *args, **kwargs):
        case = Case(*args, **kwargs)
        self.cases.append(case)
        if case.result:
            self.success_cases.append(case)
        else:
            self.failed_cases.append(case)


    def progress(self, name, cur, sum):
        if not self.show_progress: return

        if platform.system() == "Windows":
            cur = float(cur)
            sum = float(sum)
            bar = self._bar if hasattr(self, '_bar') else None
            if bar == None or bar['title'] != name:
                bar = {'title': name, 'value': cur, 'max_value': sum}
                self._bar = bar
            if (cur / sum) - (bar['value'] / bar['max_value']) > 0.1 or cur == sum:
                bar['value'] = cur
                bar['max_value'] = sum
                print('%s: %d%%' % (bar['title'], (bar['value'] / bar['max_value']) * 100.0))

        else:
            def get_bar(title, max_value):
                bar = self._bar if hasattr(self, '_bar') else None
                if bar == None or bar.title != title:
                    bar = Bar(max_value=max_value, title=title)
                    bar.cursor.clear_lines(2)  # Make some room
                    bar.cursor.save()  # Mark starting line
                self._bar = bar
                return bar

            bar = get_bar(name, sum)
            bar.cursor.restore()
            bar.draw(value=cur)


    def output(self, filename, output_type):
        cases = None
        if output_type == 0:
            cases = self.cases
        elif output_type == 1:
            cases = self.success_cases
        else:
            cases = self.failed_cases

        if not os.path.isdir(os.path.dirname(filename)): os.makedirs(os.path.dirname(filename))
        f = codecs.open(filename, "w", "utf-8")
        content = u""
        for case in cases:
            content += u'{0}\n'.format(case)
        f.write(content)
        f.close()



