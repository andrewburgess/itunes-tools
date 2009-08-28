using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Interfaces.View;

namespace Playcount_Updater
{
	class Program : PlaycountUpdaterView
	{
		static void Main(string[] args)
		{
			var program = new Program();
			program.Run();

			Console.ReadLine();
		}

		public void Run()
		{
			var controller = new PlaycountUpdaterController(this);

		}
	}
}
